const express = require("express");
const sseExpress = require("sse-express");
const EventEmitter = require("events");
const app = express();
const { createClient } = require("redis");

app.use(express.json());

const broker = createClient({ url: process.env.REDIS_URL });
const subscriber = createClient({ url: process.env.REDIS_URL });
const PUBLIC_KEYS = ["ticks", "speed", "parkingSlot", "mode"];

const emitter = new EventEmitter();

PUBLIC_KEYS.forEach((k) => {
  const channel = "__keyspace@0__:" + k;
  console.log("channel", channel);
  subscriber.subscribe(channel, (eventName) => {
    console.log("eventname", eventName);
    if (eventName === "set") {
      broker
        .get(k)
        .then((value) => {
          emitter.emit("message", [k, value]);
        })
        .catch(console.error);
    }
  });
});

app.post("/api/action", (req, res) => {
  const { action, args } = req.body;
  broker
    .get("mode")
    .then((mode) => {
      if (action === "control") {
        const x = parseFloat(args[0]);
        const y = parseFloat(args[1]);
        broker.set("control_x", x);
        broker.set("control_y", y);
        if (mode !== "control") broker.set("mode", "control");
      } else if (action === "drive" && mode != "self-driving") {
        broker.set("mode", "self-driving");
      } else if (action == "park" && mode != "self-parking") {
        broker.set("mode", "self-parking");
      } else if (mode != "idle") {
        broker.set("mode", "idle");
      }
      res.send({ action });
    })
    .catch(() => res.status(500).send("internal_error"));
});

app.get("/api/events", sseExpress, (req, res) => {
  PUBLIC_KEYS.forEach((k) => {
    broker
      .get(k)
      .then((value) => {
        res.sse("message", [k, value]);
      })
      .catch(console.error);
  });
  const subscription = (message) => {
    res.sse("message", message);
  };
  emitter.on("message", subscription);
  req.on("close", () => {
    emitter.off("message", subscription);
  });
});

app.get("/api/live", (req, res) => {
  res.writeHead(200, {
    "Cache-Control":
      "no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0",
    Pragma: "no-cache",
    Connection: "close",
    "Content-Type": "multipart/x-mixed-replace; boundary=--frame",
  });
  const subscription = (frame) => {
    res.write("--frame\r\n");
    res.write("Content-Type: image/jpeg\n");
    res.write(`Content-length:${frame.length}\n\n`)
    res.write(frame);
    res.end();
  };
  subscriber.subscribe("video_feed_original", subscription);
  req.on("close", () => {
    subscriber.unsubscribe("video_feed_original", subscription);
  });
});

Promise.all([broker.connect(), subscriber.connect()])
  .then(() => {
    console.log("Connected to redis");
    app.listen(process.env.PORT || 80, () => {
      console.log(`Server running on port ${process.env.PORT || 80}`);
    });
  })
  .catch(() => {
    console.log("Failed to connect to redis!");
  });
