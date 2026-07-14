/**
 * Shared stylized lower-48 geometry used by the map components.
 *
 * Coordinates use an equirectangular projection into a 1000x620 viewBox:
 * x = (lon + 125) * 940 / 59 + 30, y = (49 - lat) * 560 / 25 + 30.
 */

export const US_VIEWBOX = {width: 1000, height: 620};

// Simplified outline traced from projected boundary landmarks (49th
// parallel, Great Lakes, Atlantic seaboard, Florida, Gulf coast, Mexican
// border, Pacific coast).
export const US_OUTLINE = [
  'M 62 30',
  'L 506 30 L 604 48 L 678 86 L 672 102 L 706 131 L 698 180 L 691 194',
  'L 763 164 L 798 151 L 827 120 L 882 120 L 919 66 L 956 124 L 903 151',
  'L 892 180 L 843 218 L 827 270 L 811 303 L 819 339 L 733 411 L 725 447',
  'L 739 491 L 741 563 L 718 543 L 706 503 L 667 462 L 620 447 L 600 478',
  'L 511 471 L 474 547 L 436 512 L 377 478 L 325 415 L 253 427 L 194 395',
  'L 156 400 L 138 373 L 102 357 L 70 281 L 40 223 L 40 158 L 46 90',
  'L 35 43 Z',
].join(' ');

export const US_OUTLINE_LENGTH = 3400; // over-estimate for dash animation

export interface MapPoint {
  name: string;
  x: number;
  y: number;
  labelDx?: number;
  labelDy?: number;
}

export const BASINS: MapPoint[] = [
  {name: 'Permian', x: 395, y: 413, labelDy: 36},
  {name: 'Eagle Ford', x: 452, y: 489, labelDy: 36},
  {name: 'Haynesville', x: 526, y: 406, labelDy: 36},
  {name: 'Anadarko', x: 452, y: 332, labelDy: -24},
  {name: 'DJ Basin', x: 357, y: 220, labelDy: -24},
  {name: 'Uinta', x: 269, y: 227, labelDy: -24, labelDx: -14},
  {name: 'Bakken', x: 381, y: 52, labelDy: 38},
  {name: 'Appalachian', x: 739, y: 220, labelDy: -24},
];
