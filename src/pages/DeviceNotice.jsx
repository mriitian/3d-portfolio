import React, { useState } from "react";
import useMediaQuery from "../hooks/useMediaQuery";
import { SMALL_SCREEN_QUERY } from "../game/device";

const STORAGE_KEY = "device-notice-dismissed";

const wasDismissed = () => {
  try {
    return sessionStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false;
  }
};

// shown on small screens, where the gamified version is not offered
const DeviceNotice = () => {
  const isSmall = useMediaQuery(SMALL_SCREEN_QUERY);
  const [dismissed, setDismissed] = useState(wasDismissed);

  if (!isSmall || dismissed) return null;

  const close = () => {
    setDismissed(true);
    try {
      sessionStorage.setItem(STORAGE_KEY, "1");
    } catch {
      // storage can be blocked; the notice just comes back next visit
    }
  };

  return (
    <div className="fixed bottom-4 inset-x-4 z-30 mx-auto max-w-md rounded-2xl p-[1px] green-pink-gradient shadow-card">
      <div className="flex items-start gap-3 rounded-2xl bg-tertiary px-4 py-3">
        <p className="flex-1 text-[14px] text-white-100">
          <span className="font-bold text-white">Want the gamified version?</span>{" "}
          Switch to a laptop or desktop to drive around my 3D world.
        </p>
        <button
          onClick={close}
          aria-label="Dismiss"
          className="text-secondary hover:text-white text-[18px] leading-none"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default DeviceNotice;
