import express from "express";
import crypto from "crypto";
import { spawn } from "child_process";
import fs from "fs";
import path from "path";

const app = express();
app.use(express.json());

const APP_SECRET = process.env.APP_SECRET || "change_me";
const BASE_IMAGE = process.env.BASE_IMAGE || "/vm-images/base.qcow2";
const VM_STATE_DIR = process.env.VM_STATE_DIR || "/vm-state";

const sessions = new Map();

function sign(data) {
  return crypto.createHmac("sha256", APP_SECRET).update(data).digest("hex");
}

function makeAccessToken() {
  const exp = Date.now() + 1000 * 60 * 60 * 24 * 30;
  const nonce = crypto.randomUUID();
  const payload = `${exp}.${nonce}`;
  const sig = sign(payload);
  return `${payload}.${sig}`;
}

function verifyAccessToken(token) {
  const parts = token.split(".");
  if (parts.length < 3) return false;
  const exp = Number(parts[0]);
  const nonce = parts.slice(1, -1).join(".");
  const sig = parts[parts.length - 1];
  const payload = `${exp}.${nonce}`;
  if (Date.now() > exp) return false;
  return crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(sign(payload)));
}

function requireAccess(req, res, next) {
  const token = req.query.access || req.headers["x-access-token"];
  if (!token || !verifyAccessToken(token)) {
    return res.status(403).json({ error: "Forbidden" });
  }
  next();
}

function choosePort() {
  return Math.floor(5902 + Math.random() * 80);
}

app.get("/auth/link", (req, res) => {
  const token = makeAccessToken();
  res.json({ access: token, url: `/index.html?access=${encodeURIComponent(token)}` });
});

app.post("/session/start", requireAccess, (req, res) => {
  const sid = crypto.randomUUID();
  const vncPort = choosePort();
  fs.mkdirSync(VM_STATE_DIR, { recursive: true });
  const diskPath = path.join(VM_STATE_DIR, `${sid}.qcow2`);

  spawn("qemu-img", ["create", "-f", "qcow2", "-b", BASE_IMAGE, diskPath]);

  const qemuArgs = [
    "-enable-kvm",
    "-m", "4096",
    "-smp", "2",
    "-drive", `file=${diskPath},if=virtio`,
    "-vnc", `0.0.0.0:${vncPort - 5900}`,
    "-display", "none"
  ];

  const proc = spawn("qemu-system-x86_64", qemuArgs, { stdio: "ignore" });
  sessions.set(sid, { pid: proc.pid, vncPort, diskPath });

  proc.on("exit", () => sessions.delete(sid));

  const viewerUrl = `/novnc/vnc.html?host=${req.hostname}&port=443&path=wsproxy/${sid}&autoconnect=true`;

  res.json({ sid, viewerUrl });
});

app.post("/session/stop", requireAccess, (req, res) => {
  const { sid } = req.body;
  const s = sessions.get(sid);
  if (!s) return res.status(404).json({ error: "not found" });
  process.kill(s.pid, "SIGTERM");
  res.json({ ok: true });
});

app.get("/session/list", requireAccess, (req, res) => {
  res.json({ sessions: [...sessions.entries()].map(([sid, s]) => ({ sid, ...s })) });
});

app.listen(3000, () => console.log("API listening on 3000"));
