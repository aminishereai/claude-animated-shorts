import { Composition, registerRoot, getInputProps } from "remotion";
import React from "react";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";
const p = getInputProps() as any;
const Root: React.FC = () => React.createElement(Composition, { id: "BridgeShort", component: BridgeShort as any, durationInFrames: BRIDGE_FRAMES, fps: 30, width: p.w ?? 1080, height: p.h ?? 1920 });
registerRoot(Root);
