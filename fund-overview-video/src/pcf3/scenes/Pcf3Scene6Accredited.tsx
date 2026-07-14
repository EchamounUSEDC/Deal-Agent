import React from 'react';
import {AccreditedInvestorScene} from '../components/AccreditedInvestorScene';
import {pcf3SceneWindow} from '../timing';

const {durationInFrames} = pcf3SceneWindow('scene6Accredited');

/** 0:46–0:53 — Accredited-investor qualification screen. */
export const Pcf3Scene6Accredited: React.FC = () => {
  return <AccreditedInvestorScene durationInFrames={durationInFrames} />;
};
