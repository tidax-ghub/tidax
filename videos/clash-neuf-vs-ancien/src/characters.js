// Personnages et décor du clash, en SVG (viewBox 1080×1920, plein cadre).
// Chaque perso expose des groupes animables : .mouth (bouche), .lid (paupières),
// .arm-mic (bras micro), .arm-fist (poing).
(function () {
  const INK = "#1b1410";

  function mic(x, y, rot) {
    return `<g transform="translate(${x} ${y}) rotate(${rot})">
      <rect x="-15" y="20" width="30" height="150" rx="12" fill="#1d1d1f" stroke="${INK}" stroke-width="6"/>
      <rect x="-19" y="12" width="38" height="20" rx="6" fill="#3a3a3e" stroke="${INK}" stroke-width="5"/>
      <circle cx="0" cy="-14" r="44" fill="#2a2a2e" stroke="${INK}" stroke-width="7"/>
      <path d="M-34 -30 L34 -30 M-40 -14 L40 -14 M-34 2 L34 2 M-20 -50 L-20 22 M0 -56 L0 28 M20 -50 L20 22" stroke="#55555b" stroke-width="4"/>
      <ellipse cx="-14" cy="-32" rx="12" ry="7" fill="#77777f" opacity=".7"/>
    </g>`;
  }

  function arm(d, fill, w) {
    return `<path d="${d}" fill="none" stroke="${INK}" stroke-width="${w + 14}" stroke-linecap="round"/>
            <path d="${d}" fill="none" stroke="${fill}" stroke-width="${w}" stroke-linecap="round"/>`;
  }

  function glove(x, y, r, fill) {
    return `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${INK}" stroke-width="7"/>
      <path d="M${x - r * 0.55} ${y - r * 0.2} Q${x} ${y - r * 0.55} ${x + r * 0.55} ${y - r * 0.2}" fill="none" stroke="${INK}" stroke-width="5" stroke-linecap="round"/>
      <path d="M${x - r * 0.5} ${y + r * 0.15} Q${x} ${y - r * 0.15} ${x + r * 0.5} ${y + r * 0.15}" fill="none" stroke="${INK}" stroke-width="5" stroke-linecap="round"/>`;
  }

  function mouth(cx, cy, rx, ry) {
    return `<g class="mouth" data-cx="${cx}" data-cy="${cy}">
      <ellipse cx="${cx}" cy="${cy + ry * 0.5}" rx="${rx}" ry="${ry}" fill="#3a0f12" stroke="${INK}" stroke-width="7"/>
      <ellipse cx="${cx}" cy="${cy + ry * 1.05}" rx="${rx * 0.55}" ry="${ry * 0.38}" fill="#d9555c"/>
      <rect x="${cx - rx * 0.62}" y="${cy - ry * 0.45}" width="${rx * 1.24}" height="${ry * 0.42}" rx="6" fill="#f4efe0"/>
    </g>`;
  }

  function eye(cx, cy, rx, ry, iris, lidFill) {
    return `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#fbfaf4" stroke="${INK}" stroke-width="7"/>
      <circle cx="${cx + 4}" cy="${cy + 6}" r="${ry * 0.52}" fill="${iris}" stroke="${INK}" stroke-width="4"/>
      <circle cx="${cx + 4}" cy="${cy + 6}" r="${ry * 0.24}" fill="#0b0b0b"/>
      <circle cx="${cx - 6}" cy="${cy - 6}" r="${ry * 0.12}" fill="#fff"/>
      <g class="lid" data-cx="${cx}" data-cy="${cy - ry}">
        <path d="M${cx - rx - 3} ${cy} A${rx + 3} ${ry + 3} 0 0 1 ${cx + rx + 3} ${cy} Z" fill="${lidFill}" stroke="${INK}" stroke-width="6"/>
      </g>`;
  }

  function legs(pants, shoe, sole) {
    return `<rect x="415" y="1660" width="62" height="120" fill="${pants}" stroke="${INK}" stroke-width="7"/>
      <rect x="603" y="1660" width="62" height="120" fill="${pants}" stroke="${INK}" stroke-width="7"/>
      <path d="M360 1810 Q360 1758 430 1758 L478 1758 Q500 1800 490 1818 Z" fill="${shoe}" stroke="${INK}" stroke-width="7"/>
      <path d="M720 1810 Q720 1758 650 1758 L602 1758 Q580 1800 590 1818 Z" fill="${shoe}" stroke="${INK}" stroke-width="7"/>
      <rect x="352" y="1806" width="144" height="16" rx="7" fill="${sole}" stroke="${INK}" stroke-width="6"/>
      <rect x="584" y="1806" width="144" height="16" rx="7" fill="${sole}" stroke="${INK}" stroke-width="6"/>`;
  }

  // ---------- L'ANCIEN : immeuble haussmannien de 1890 ----------
  function ancien() {
    const stone = "#ead9b0";
    let joints = "";
    for (let y = 560; y < 1690; y += 62) joints += `<line x1="296" y1="${y}" x2="784" y2="${y}" stroke="#cdb886" stroke-width="3"/>`;
    for (let y = 560, k = 0; y < 1690; y += 62, k++)
      for (let x = 330 + (k % 2) * 60; x < 780; x += 120)
        joints += `<line x1="${x}" y1="${y}" x2="${x}" y2="${y + 62}" stroke="#cdb886" stroke-width="3"/>`;
    let zinc = "";
    for (let x = 350; x <= 730; x += 38) zinc += `<line x1="${x}" y1="305" x2="${x + (x - 540) * 0.28}" y2="505" stroke="#46525d" stroke-width="4"/>`;
    const win = (x, y, w, h) => `<g>
      <rect x="${x - 10}" y="${y - 10}" width="${w + 20}" height="${h + 20}" fill="#d8c393" stroke="${INK}" stroke-width="6"/>
      <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#2e4a68" stroke="${INK}" stroke-width="6"/>
      <path d="M${x + w / 2} ${y} V${y + h} M${x} ${y + h * 0.38} H${x + w}" stroke="#efe6cf" stroke-width="7"/>
      <path d="M${x + 8} ${y + 10} L${x + 26} ${y + 10} L${x + 8} ${y + 40} Z" fill="#7fa6c9" opacity=".7"/>
      <rect x="${x - 20}" y="${y + h + 8}" width="${w + 40}" height="12" fill="#d8c393" stroke="${INK}" stroke-width="5"/>
    </g>`;
    let rail = "";
    for (let x = 318; x < 770; x += 30) rail += `<path d="M${x} 985 V1035 M${x} 1000 q15 12 30 0" stroke="#1d1d1d" stroke-width="5" fill="none"/>`;
    return `
    <g class="legs">${legs("#3d3530", "#5b3a22", "#2b1a10")}</g>
    <g class="body">
      <rect x="290" y="505" width="500" height="1185" rx="16" fill="${stone}" stroke="${INK}" stroke-width="9"/>
      ${joints}
      <rect x="300" y="545" width="16" height="1140" fill="#d8c393"/><rect x="764" y="545" width="16" height="1140" fill="#d8c393"/>
      <rect x="380" y="200" width="56" height="120" fill="#b5634a" stroke="${INK}" stroke-width="7"/>
      <rect x="372" y="190" width="72" height="22" fill="#9a4f3a" stroke="${INK}" stroke-width="6"/>
      <rect x="652" y="215" width="56" height="105" fill="#b5634a" stroke="${INK}" stroke-width="7"/>
      <rect x="644" y="205" width="72" height="22" fill="#9a4f3a" stroke="${INK}" stroke-width="6"/>
      <path d="M268 512 L335 300 L745 300 L812 512 Z" fill="#5f6d79" stroke="${INK}" stroke-width="9" stroke-linejoin="round"/>
      ${zinc}
      <path d="M392 470 V400 Q430 355 468 400 V470 Z" fill="#e6d5aa" stroke="${INK}" stroke-width="6"/>
      <rect x="408" y="410" width="44" height="58" fill="#2e4a68" stroke="${INK}" stroke-width="5"/>
      <path d="M612 470 V400 Q650 355 688 400 V470 Z" fill="#e6d5aa" stroke="${INK}" stroke-width="6"/>
      <rect x="628" y="410" width="44" height="58" fill="#2e4a68" stroke="${INK}" stroke-width="5"/>
      <rect x="262" y="500" width="556" height="30" rx="6" fill="#d8c393" stroke="${INK}" stroke-width="7"/>
      <path d="M262 530 h556" stroke="#b9a473" stroke-width="5"/>
      <!-- visage -->
      <path d="M368 720 q20 14 40 4 M672 720 q-20 14 -40 4 M380 742 q18 10 34 2 M700 742 q-18 10 -34 2" stroke="#b9a473" stroke-width="5" fill="none"/>
      ${eye(450, 655, 74, 64, "#6f8a58", "#d6c08e")}
      ${eye(630, 655, 74, 64, "#6f8a58", "#d6c08e")}
      <path d="M362 578 Q420 548 512 600" stroke="${INK}" stroke-width="34" stroke-linecap="round" fill="none"/>
      <path d="M718 578 Q660 548 568 600" stroke="${INK}" stroke-width="34" stroke-linecap="round" fill="none"/>
      <path d="M362 578 Q420 548 512 600" stroke="#f3f1ea" stroke-width="22" stroke-linecap="round" fill="none"/>
      <path d="M718 578 Q660 548 568 600" stroke="#f3f1ea" stroke-width="22" stroke-linecap="round" fill="none"/>
      ${mouth(540, 846, 92, 64)}
      <ellipse cx="540" cy="752" rx="40" ry="48" fill="#e2b48c" stroke="${INK}" stroke-width="7"/>
      <ellipse cx="528" cy="738" rx="12" ry="9" fill="#f3d2b2"/>
      <path d="M420 832 Q470 780 540 810 Q610 780 660 832 Q640 868 600 852 Q570 842 540 852 Q510 842 480 852 Q440 868 420 832 Z" fill="#f1f0ea" stroke="${INK}" stroke-width="7"/>
      <path d="M760 560 L738 618 L757 660 L728 735 L744 772" stroke="${INK}" stroke-width="6" fill="none" stroke-linejoin="round"/>
      <path d="M316 1180 L340 1230 L326 1270" stroke="${INK}" stroke-width="5" fill="none"/>
      <!-- balcon fer forgé -->
      <rect x="300" y="968" width="480" height="16" fill="#262626" stroke="${INK}" stroke-width="4"/>
      ${rail}
      <rect x="300" y="1032" width="480" height="12" fill="#262626"/>
      ${win(330, 1085, 92, 160)}${win(494, 1085, 92, 160)}${win(658, 1085, 92, 160)}
      ${win(330, 1310, 92, 150)}${win(658, 1310, 92, 150)}
      <path d="M478 1690 V1530 Q540 1462 602 1530 V1690 Z" fill="#5a3522" stroke="${INK}" stroke-width="8"/>
      <path d="M540 1500 V1690" stroke="${INK}" stroke-width="5"/>
      <circle cx="526" cy="1610" r="7" fill="#d9b44a"/><circle cx="554" cy="1610" r="7" fill="#d9b44a"/>
      <rect x="490" y="1395" width="100" height="44" rx="8" fill="#1f3c74" stroke="${INK}" stroke-width="5"/>
      <text data-layout-ignore x="540" y="1428" text-anchor="middle" font-family="Anton" font-size="30" fill="#fff">1890</text>
      <g fill="#4f8a3a" stroke="${INK}" stroke-width="4">
        <circle cx="304" cy="1560" r="22"/><circle cx="318" cy="1600" r="20"/><circle cx="300" cy="1640" r="24"/><circle cx="326" cy="1675" r="20"/><circle cx="310" cy="1520" r="16"/>
      </g>
    </g>
    <g class="arm-fist">${arm("M786 1080 Q900 1010 838 912", stone, 54)}${glove(836, 900, 52, "#f7f3ea")}</g>
    <g class="arm-mic">${arm("M294 1090 Q170 1010 300 930", stone, 54)}${mic(372, 880, 28)}${glove(316, 930, 50, "#f7f3ea")}</g>`;
  }

  // ---------- LE NEUF : résidence neuve RE2020 ----------
  function neuf() {
    let solar = "";
    for (let i = 0; i < 4; i++) {
      const x = 318 + i * 114;
      solar += `<path d="M${x} 410 L${x + 22} 318 L${x + 118} 318 L${x + 98} 410 Z" fill="#1d3b78" stroke="${INK}" stroke-width="6"/>
        <path d="M${x + 11} 364 L${x + 108} 364 M${x + 46} 318 L${x + 38} 410 M${x + 78} 318 L${x + 70} 410" stroke="#6f9ad6" stroke-width="3"/>`;
    }
    let wood = "";
    for (let x = 652; x < 772; x += 20) wood += `<line x1="${x}" y1="1085" x2="${x}" y2="1690" stroke="#a86d36" stroke-width="4"/>`;
    const glass = (x, y, w, h) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#8fd3f4" stroke="${INK}" stroke-width="6"/>
      <path d="M${x + 14} ${y + h - 14} L${x + w * 0.55} ${y + 14} L${x + w * 0.75} ${y + 14} L${x + 30} ${y + h - 14} Z" fill="#e8f7ff" opacity=".75"/>
      <path d="M${x + w / 2} ${y} V${y + h}" stroke="#4b5563" stroke-width="5"/>`;
    return `
    <g class="legs">${legs("#22314f", "#f5f5f5", "#e2483d")}</g>
    <g class="body">
      ${solar}
      <rect x="292" y="412" width="496" height="40" rx="12" fill="#cfd6de" stroke="${INK}" stroke-width="7"/>
      <rect x="300" y="440" width="480" height="1250" rx="24" fill="#f4f6f9" stroke="${INK}" stroke-width="9"/>
      <rect x="640" y="1080" width="134" height="604" fill="#c98a4b" stroke="${INK}" stroke-width="6"/>${wood}
      <g fill="#5cb85c" stroke="${INK}" stroke-width="5">
        <circle cx="330" cy="436" r="20"/><circle cx="362" cy="428" r="24"/><circle cx="740" cy="430" r="22"/><circle cx="712" cy="438" r="18"/>
      </g>
      <!-- visage -->
      <path d="M380 568 Q440 532 506 560" stroke="${INK}" stroke-width="24" stroke-linecap="round" fill="none"/>
      <path d="M700 552 Q640 520 574 552" stroke="${INK}" stroke-width="24" stroke-linecap="round" fill="none"/>
      <path d="M360 610 H720 V636 Q712 720 640 722 Q580 722 560 660 L520 660 Q500 722 440 722 Q368 720 360 636 Z" fill="#141821" stroke="${INK}" stroke-width="8"/>
      <path d="M392 632 L432 632 L400 700 Z M600 632 L640 632 L608 700 Z" fill="#5b7fb5" opacity=".55"/>
      <path d="M360 616 H336 M720 616 H744" stroke="${INK}" stroke-width="10"/>
      ${mouth(540, 816, 104, 62)}
      <path d="M432 806 Q540 846 650 798" stroke="${INK}" stroke-width="8" fill="none" stroke-linecap="round"/>
      <path d="M648 790 q16 6 18 22" stroke="${INK}" stroke-width="7" fill="none" stroke-linecap="round"/>
      <!-- chaîne RE2020 -->
      <path d="M380 900 Q540 1040 700 900" fill="none" stroke="#8a6512" stroke-width="20"/>
      <path d="M380 900 Q540 1040 700 900" fill="none" stroke="#f2c230" stroke-width="13" stroke-dasharray="16 7"/>
      <circle cx="540" cy="1010" r="62" fill="#f2c230" stroke="${INK}" stroke-width="7"/>
      <circle cx="540" cy="1010" r="48" fill="none" stroke="#c9961a" stroke-width="4"/>
      <text data-layout-ignore x="540" y="1004" text-anchor="middle" font-family="Anton" font-size="28" fill="${INK}">RE</text>
      <text data-layout-ignore x="540" y="1036" text-anchor="middle" font-family="Anton" font-size="28" fill="${INK}">2020</text>
      ${glass(330, 1100, 130, 190)}${glass(480, 1100, 130, 190)}
      <rect x="318" y="1280" width="304" height="58" fill="#bfe6f7" opacity=".7" stroke="${INK}" stroke-width="5"/>
      <g fill="#5cb85c" stroke="${INK}" stroke-width="4"><circle cx="352" cy="1272" r="20"/><circle cx="380" cy="1262" r="16"/><circle cx="596" cy="1268" r="20"/></g>
      ${glass(330, 1370, 130, 170)}${glass(480, 1370, 130, 170)}
      <rect x="470" y="1560" width="140" height="130" fill="#2a3446" stroke="${INK}" stroke-width="7"/>
      <path d="M484 1576 L520 1576 L490 1650 Z" fill="#6c86ad" opacity=".6"/>
      <rect x="626" y="1600" width="20" height="30" rx="4" fill="#4b5563"/>
      <circle cx="705" cy="1000" r="30" fill="#17804a" stroke="${INK}" stroke-width="5"/>
      <text data-layout-ignore x="705" y="1013" text-anchor="middle" font-family="Anton" font-size="34" fill="#fff">A</text>
    </g>
    <g class="arm-fist">${arm("M296 1090 Q180 1020 244 916", "#f4f6f9", 54)}${glove(244, 904, 52, "#2a2f3a")}</g>
    <g class="arm-mic">${arm("M784 1090 Q910 1010 780 930", "#f4f6f9", 54)}${mic(708, 880, -28)}${glove(764, 930, 50, "#2a2f3a")}</g>`;
  }

  // ---------- LE MC ----------
  function mc() {
    const skin = "#f2b27f";
    return `
    <g class="legs">${legs("#20345e", "#fafafa", "#c33")}</g>
    <g class="body">
      <path d="M330 1700 V1180 Q330 1080 430 1060 L650 1060 Q750 1080 750 1180 V1700 Z" fill="#f3ead4" stroke="${INK}" stroke-width="9"/>
      <path d="M430 1060 Q540 1170 650 1060" fill="${skin}" stroke="#20345e" stroke-width="22"/>
      <path d="M330 1180 Q330 1080 430 1060 M750 1180 Q750 1080 650 1060" fill="none" stroke="#20345e" stroke-width="22"/>
      <path d="M440 1080 Q540 1200 640 1080" fill="none" stroke="#e8b923" stroke-width="16" stroke-dasharray="14 6"/>
      <text data-layout-ignore x="540" y="1655" text-anchor="middle" font-family="Anton" font-size="170" fill="#d0342c" stroke="${INK}" stroke-width="8">MC</text>
      <rect x="440" y="960" width="200" height="120" fill="${skin}" stroke="${INK}" stroke-width="8"/>
      <ellipse cx="330" cy="720" rx="40" ry="62" fill="${skin}" stroke="${INK}" stroke-width="8"/>
      <ellipse cx="750" cy="720" rx="40" ry="62" fill="${skin}" stroke="${INK}" stroke-width="8"/>
      <path d="M340 640 Q340 420 540 420 Q740 420 740 640 L740 800 Q740 990 540 990 Q340 990 340 800 Z" fill="${skin}" stroke="${INK}" stroke-width="9"/>
      <path d="M380 840 Q400 970 540 975 Q680 970 700 840 Q660 900 540 905 Q420 900 380 840 Z" fill="#8a5a3a" opacity=".55"/>
      <path d="M326 560 Q330 380 540 372 Q750 380 754 560 Q540 520 326 560 Z" fill="#22335e" stroke="${INK}" stroke-width="9"/>
      <path d="M326 560 Q540 520 754 560" fill="none" stroke="#14203d" stroke-width="12"/>
      <path d="M680 440 Q800 470 820 560 Q770 545 720 520" fill="#22335e" stroke="${INK}" stroke-width="8"/>
      <circle cx="540" cy="380" r="14" fill="#14203d"/>
      ${eye(462, 650, 62, 62, "#3a2a1a", skin)}
      ${eye(618, 650, 62, 62, "#3a2a1a", skin)}
      <path d="M402 572 Q460 552 512 576 M568 576 Q620 552 678 572" stroke="${INK}" stroke-width="16" stroke-linecap="round" fill="none"/>
      <path d="M540 700 Q520 770 560 776" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>
      ${mouth(540, 830, 78, 46)}
    </g>
    <g class="arm-fist">${arm("M744 1180 Q840 1240 790 1330", skin, 58)}${glove(790, 1340, 48, skin)}</g>
    <g class="arm-mic">${arm("M336 1180 Q230 1050 330 960", skin, 58)}${mic(410, 900, 30)}${glove(344, 960, 50, skin)}</g>`;
  }

  // ---------- Décor : scène, foule, projecteurs, parquet ----------
  function stage() {
    let s = 7;
    const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    let crowdBack = "", crowdFront = "";
    for (let i = 0; i < 26; i++) {
      const x = -20 + i * 44 + rnd() * 20, y = 1300 + rnd() * 50, r = 26 + rnd() * 8;
      crowdBack += `<circle cx="${x}" cy="${y}" r="${r}"/><rect x="${x - 34}" y="${y + 18}" width="68" height="240" rx="28"/>`;
      if (rnd() > 0.45) crowdBack += `<path class="hand" d="M${x + 18} ${y + 30} L${x + 40 + rnd() * 30} ${y - 120 - rnd() * 60}" stroke-width="18" stroke-linecap="round"/>`;
    }
    for (let i = 0; i < 18; i++) {
      const x = -10 + i * 64 + rnd() * 24, y = 1380 + rnd() * 50, r = 34 + rnd() * 8;
      crowdFront += `<circle cx="${x}" cy="${y}" r="${r}"/><rect x="${x - 44}" y="${y + 24}" width="88" height="220" rx="34"/>`;
      if (rnd() > 0.4) crowdFront += `<path class="hand" d="M${x - 20} ${y + 40} L${x - 50 - rnd() * 30} ${y - 120 - rnd() * 70}" stroke-width="22" stroke-linecap="round"/>`;
    }
    let planks = "";
    for (let y = 1560, h = 26; y < 1920; y += h, h *= 1.14) planks += `<line x1="0" y1="${y}" x2="1080" y2="${y}" stroke="#6b3615" stroke-width="5"/>`;
    for (let k = -6; k <= 6; k++) planks += `<line x1="${540 + k * 70}" y1="1534" x2="${540 + k * 230}" y2="1920" stroke="#7a3f19" stroke-width="3" opacity=".45"/>`;
    return `<svg data-layout-allow-overflow viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1530"/><stop offset=".7" stop-color="#1c3961"/><stop offset="1" stop-color="#22466f"/></linearGradient>
        <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
        <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a4a1f"/><stop offset="1" stop-color="#b8662d"/></linearGradient>
        <pattern id="dots" width="60" height="60" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="2" fill="#fff" opacity=".08"/><circle cx="40" cy="38" r="1.6" fill="#fff" opacity=".06"/></pattern>
      </defs>
      <rect width="1080" height="1920" fill="url(#sky)"/>
      <rect width="1080" height="1400" fill="url(#dots)"/>
      <g class="beams">
        <path class="beam beam-l" d="M120 -20 L220 -20 L520 1540 L-160 1540 Z" fill="url(#beam)"/>
        <path class="beam beam-r" d="M860 -20 L960 -20 L1240 1540 L560 1540 Z" fill="url(#beam)"/>
      </g>
      <g class="crowd-back" fill="#132649" stroke="#132649">${crowdBack}</g>
      <g class="crowd-front" fill="#0b1833" stroke="#0b1833">${crowdFront}</g>
      <rect x="0" y="1520" width="1080" height="400" fill="url(#floor)"/>
      ${planks}
      <rect x="0" y="1512" width="1080" height="22" fill="#5a2c10"/>
      <ellipse cx="540" cy="1800" rx="330" ry="46" fill="#000" opacity=".28"/>
    </svg>`;
  }

  function character(kind) {
    const body = { ancien, neuf, mc }[kind]();
    return `<svg viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg">${body}</svg>`;
  }

  window.CLASH_ART = { stage, character };
})();
