/* ============================================
   March Madness Bracket Optimizer
   Data + Interactivity
   ============================================ */

(function () {
  'use strict';

  /* ---- 2026 Tournament Data ---- */

  // Complete bracket: each region has 16 seeds in matchup order
  // Matchup pairs: [1,16], [8,9], [5,12], [4,13], [6,11], [3,14], [7,10], [2,15]
  const REGIONS = {
    east: {
      name: 'East',
      teams: [
        { seed: 1, name: 'Duke' },
        { seed: 16, name: 'Siena' },
        { seed: 8, name: 'Ohio State' },
        { seed: 9, name: 'TCU' },
        { seed: 5, name: "St. John's" },
        { seed: 12, name: 'Northern Iowa' },
        { seed: 4, name: 'Kansas' },
        { seed: 13, name: 'Cal Baptist' },
        { seed: 6, name: 'Louisville' },
        { seed: 11, name: 'South Florida' },
        { seed: 3, name: 'Michigan State' },
        { seed: 14, name: 'North Dakota St' },
        { seed: 7, name: 'UCLA' },
        { seed: 10, name: 'UCF' },
        { seed: 2, name: 'UConn' },
        { seed: 15, name: 'Furman' }
      ]
    },
    west: {
      name: 'West',
      teams: [
        { seed: 1, name: 'Arizona' },
        { seed: 16, name: 'LIU' },
        { seed: 8, name: 'Villanova' },
        { seed: 9, name: 'Utah State' },
        { seed: 5, name: 'Wisconsin' },
        { seed: 12, name: 'High Point' },
        { seed: 4, name: 'Arkansas' },
        { seed: 13, name: 'Hawaii' },
        { seed: 6, name: 'BYU' },
        { seed: 11, name: 'Texas' },
        { seed: 3, name: 'Gonzaga' },
        { seed: 14, name: 'Kennesaw St' },
        { seed: 7, name: 'Miami (FL)' },
        { seed: 10, name: 'Missouri' },
        { seed: 2, name: 'Purdue' },
        { seed: 15, name: 'Queens' }
      ]
    },
    midwest: {
      name: 'Midwest',
      teams: [
        { seed: 1, name: 'Michigan' },
        { seed: 16, name: 'Howard' },
        { seed: 8, name: 'Georgia' },
        { seed: 9, name: 'Saint Louis' },
        { seed: 5, name: 'Texas Tech' },
        { seed: 12, name: 'Akron' },
        { seed: 4, name: 'Alabama' },
        { seed: 13, name: 'Hofstra' },
        { seed: 6, name: 'Tennessee' },
        { seed: 11, name: 'SMU' },
        { seed: 3, name: 'Virginia' },
        { seed: 14, name: 'Wright State' },
        { seed: 7, name: 'Kentucky' },
        { seed: 10, name: 'Santa Clara' },
        { seed: 2, name: 'Iowa State' },
        { seed: 15, name: 'Tennessee State' }
      ]
    },
    south: {
      name: 'South',
      teams: [
        { seed: 1, name: 'Florida' },
        { seed: 16, name: 'Lehigh' },
        { seed: 8, name: 'Clemson' },
        { seed: 9, name: 'Iowa' },
        { seed: 5, name: 'Vanderbilt' },
        { seed: 12, name: 'McNeese' },
        { seed: 4, name: 'Nebraska' },
        { seed: 13, name: 'Troy' },
        { seed: 6, name: 'North Carolina' },
        { seed: 11, name: 'VCU' },
        { seed: 3, name: 'Illinois' },
        { seed: 14, name: 'Penn' },
        { seed: 7, name: "Saint Mary's" },
        { seed: 10, name: 'Texas A&M' },
        { seed: 2, name: 'Houston' },
        { seed: 15, name: 'Idaho' }
      ]
    }
  };

  const ROUND_NAMES = [
    'Round of 64',
    'Round of 32',
    'Sweet 16',
    'Elite 8',
    'Final Four',
    'Championship'
  ];

  const ROUND_POINTS = [10, 20, 40, 80, 160, 320];

  /* ---- 4 Bracket Entries ----
     Each bracket defines picks per region as arrays of advancing teams.
     Round 1: 8 winners from 8 matchups
     Round 2: 4 winners
     Sweet 16: 2 winners
     Elite 8: 1 regional champion
     Then: Final Four matchups and champion.

     Format: { region: [R1 winners (8), R2 winners (4), S16 winners (2), E8 winner (1)] }
     Plus: finalFour: { semi1: [team1, team2], semi1Winner, semi2: [team1, team2], semi2Winner, champion }
  */

  const BRACKETS = [
    {
      id: 1,
      name: 'The Chalk',
      subtitle: 'Favorites-heavy for a medium-sized pool',
      champion: 'Duke',
      strategy: "This bracket rides the favorites. Duke is the #1 overall seed, the betting favorite at +300, and one of only a handful of teams in the last two decades to rank top-4 in both offensive and defensive efficiency (KenPom). Coach Jon Scheyer's squad has Cam Boozer, multiple projected first-round NBA picks, and an elite defense that opponents shoot under 43% against from two-point range. In a medium-sized pool of 30 to 80 entries, having one entry that tracks chalk is essential insurance. If the tournament plays out roughly according to seed, this bracket will score extremely well. The key risk is that roughly 15% of public brackets will also pick Duke, so this entry has moderate overlap with the field. We offset that with mild upset picks in the early rounds to gain a few differentiating points where we have strong conviction, including Iowa over Clemson (Clemson lost its second-leading scorer Carter Welling to a torn ACL in the ACC Tournament) and Texas A&M over Saint Mary's (the Aggies average 10 more points per game with six players in double figures).",
      regions: {
        east: {
          r1: ['Duke', 'Ohio State', "St. John's", 'Kansas', 'Louisville', 'Michigan State', 'UCLA', 'UConn'],
          r2: ['Duke', "St. John's", 'Michigan State', 'UConn'],
          s16: ['Duke', 'UConn'],
          e8: ['Duke']
        },
        west: {
          r1: ['Arizona', 'Villanova', 'Wisconsin', 'Arkansas', 'BYU', 'Gonzaga', 'Miami (FL)', 'Purdue'],
          r2: ['Arizona', 'Arkansas', 'Gonzaga', 'Purdue'],
          s16: ['Arizona', 'Purdue'],
          e8: ['Arizona']
        },
        midwest: {
          r1: ['Michigan', 'Georgia', 'Texas Tech', 'Alabama', 'Tennessee', 'Virginia', 'Kentucky', 'Iowa State'],
          r2: ['Michigan', 'Alabama', 'Tennessee', 'Iowa State'],
          s16: ['Michigan', 'Iowa State'],
          e8: ['Michigan']
        },
        south: {
          r1: ['Florida', 'Iowa', 'Vanderbilt', 'Nebraska', 'North Carolina', 'Illinois', 'Texas A&M', 'Houston'],
          r2: ['Florida', 'Vanderbilt', 'Illinois', 'Houston'],
          s16: ['Florida', 'Houston'],
          e8: ['Houston']
        }
      },
      finalFour: {
        semi1: { teams: ['Duke', 'Arizona'], winner: 'Duke' },
        semi2: { teams: ['Michigan', 'Houston'], winner: 'Duke' },
        champion: 'Duke'
      }
    },
    {
      id: 2,
      name: 'The Analytics Edge',
      subtitle: 'KenPom-driven with contrarian champion',
      champion: 'Houston',
      strategy: "Houston is this bracket's champion and the highest-conviction contrarian play available. The Cougars check every analytical box: top-5 in KenPom overall, top-5 in defensive efficiency, 13-to-1 championship odds offering strong leverage, and they sit in the South Region with the weakest #1 seed in Florida (who went 6-7 down the stretch). The clincher is geography. If Houston reaches the Elite Eight, they play at Toyota Center in Houston. That is a massive, nearly unreplicable home-court advantage in a single-elimination format. The public is heavily picking Arizona and Duke as champions, which means Houston bracket ownership will be low, perhaps 3 to 5% of a medium pool. If Houston wins it all, this bracket's 320-point champion bonus will belong to very few entries, vaulting it to the top. The rest of the bracket leans on KenPom efficiency. Arizona cruises through a favorable West draw. Iowa State's #4-ranked defense grinds through the Midwest, and UConn's tournament DNA carries them out of a loaded East. This is not a random upset bracket. It is a disciplined, analytics-first path that simply disagrees with the public on which elite team cuts down the nets.",
      regions: {
        east: {
          r1: ['Duke', 'TCU', "St. John's", 'Kansas', 'Louisville', 'Michigan State', 'UCF', 'UConn'],
          r2: ['Duke', 'Kansas', 'Michigan State', 'UConn'],
          s16: ['Duke', 'UConn'],
          e8: ['UConn']
        },
        west: {
          r1: ['Arizona', 'Utah State', 'Wisconsin', 'Arkansas', 'BYU', 'Gonzaga', 'Missouri', 'Purdue'],
          r2: ['Arizona', 'Arkansas', 'Gonzaga', 'Purdue'],
          s16: ['Arizona', 'Purdue'],
          e8: ['Arizona']
        },
        midwest: {
          r1: ['Michigan', 'Saint Louis', 'Texas Tech', 'Alabama', 'Tennessee', 'Virginia', 'Kentucky', 'Iowa State'],
          r2: ['Michigan', 'Alabama', 'Virginia', 'Iowa State'],
          s16: ['Michigan', 'Iowa State'],
          e8: ['Iowa State']
        },
        south: {
          r1: ['Florida', 'Iowa', 'Vanderbilt', 'Nebraska', 'North Carolina', 'Illinois', 'Texas A&M', 'Houston'],
          r2: ['Florida', 'Vanderbilt', 'North Carolina', 'Houston'],
          s16: ['Florida', 'Houston'],
          e8: ['Houston']
        }
      },
      finalFour: {
        semi1: { teams: ['UConn', 'Arizona'], winner: 'Arizona' },
        semi2: { teams: ['Iowa State', 'Houston'], winner: 'Houston' },
        champion: 'Houston'
      }
    },
    {
      id: 3,
      name: 'The Contrarian',
      subtitle: 'Maximum leverage for pool separation',
      champion: 'Iowa State',
      strategy: "This is the swing bracket, designed to separate from the pack if the tournament deviates even slightly from public expectation. Iowa State at 18-to-1 odds is the champion pick. The Cyclones rank #6 in KenPom overall and #4 nationally in defensive efficiency. They play a suffocating defensive style that thrives in tournament settings where possessions are precious and half-court execution matters more than regular-season point differentials. Their path through the Midwest requires getting past Michigan, but Iowa State's defensive identity is precisely the profile that can neutralize Michigan's size advantage. The critical insight is public ownership. Virtually nobody in your pool will pick Iowa State to win it all, maybe zero other entries. That means if they cut down the nets, you own 320 points that nobody else has. In a 30-to-80 entry pool, that alone is likely enough to win first place. The rest of this bracket takes calculated risks: Purdue through the West (their KenPom profile is elite and they avoid Arizona until the Elite Eight), Illinois through the South (top-10 KenPom, undervalued by the public), and Duke through the East (even contrarian brackets need some chalk to accumulate baseline points in early rounds). Every pick in this bracket has an analytical justification, but the overall portfolio is deliberately different from what 90%+ of entries will look like.",
      regions: {
        east: {
          r1: ['Duke', 'TCU', "St. John's", 'Kansas', 'South Florida', 'Michigan State', 'UCLA', 'UConn'],
          r2: ['Duke', "St. John's", 'Michigan State', 'UConn'],
          s16: ['Duke', 'Michigan State'],
          e8: ['Duke']
        },
        west: {
          r1: ['Arizona', 'Villanova', 'Wisconsin', 'Arkansas', 'Texas', 'Gonzaga', 'Miami (FL)', 'Purdue'],
          r2: ['Arizona', 'Arkansas', 'Gonzaga', 'Purdue'],
          s16: ['Arizona', 'Purdue'],
          e8: ['Purdue']
        },
        midwest: {
          r1: ['Michigan', 'Georgia', 'Akron', 'Alabama', 'Tennessee', 'Virginia', 'Kentucky', 'Iowa State'],
          r2: ['Michigan', 'Alabama', 'Tennessee', 'Iowa State'],
          s16: ['Michigan', 'Iowa State'],
          e8: ['Iowa State']
        },
        south: {
          r1: ['Florida', 'Iowa', 'Vanderbilt', 'Nebraska', 'North Carolina', 'Illinois', 'Texas A&M', 'Houston'],
          r2: ['Florida', 'Vanderbilt', 'Illinois', 'Houston'],
          s16: ['Florida', 'Illinois'],
          e8: ['Illinois']
        }
      },
      finalFour: {
        semi1: { teams: ['Duke', 'Purdue'], winner: 'Duke' },
        semi2: { teams: ['Iowa State', 'Illinois'], winner: 'Iowa State' },
        champion: 'Iowa State'
      }
    },
    {
      id: 4,
      name: 'The Dark Horse',
      subtitle: 'Expert consensus with sleeper upside',
      champion: 'Arizona',
      strategy: "Arizona is the consensus pick among ESPN experts (33 of 60 analysts picked them to win it all), and for good reason. The Wildcats are a top-3 KenPom team, ranking in the top 5 nationally in both offensive and defensive efficiency. They dominate the paint and the offensive glass, and their West Region draw is the most favorable of any #1 seed. Their path avoids the other top KenPom teams until the Final Four. While Arizona is popular among analysts, the general public tends to gravitate toward Duke and Michigan as champion picks, which means Arizona's public ownership may be lower than their true championship probability warrants. That gap between true probability and public pick rate is where expected value lives. This bracket pairs Arizona with a Michigan State sleeper run through the East, which seven ESPN analysts also endorsed. Michigan State is one of only 11 KenPom-certified championship contenders and has the shooting and defensive versatility to upset both St. John's and UConn. In the Midwest, Michigan's #1-ranked defense carries them to the Final Four. And Houston provides insurance in the South with their defensive excellence and geographical advantage. The resulting Final Four of Arizona, Michigan State, Michigan, and Houston is analytically defensible, moderately contrarian in the East slot, and gives this bracket differentiation from entries that simply pick all four #1 seeds.",
      regions: {
        east: {
          r1: ['Duke', 'Ohio State', "St. John's", 'Kansas', 'Louisville', 'Michigan State', 'UCLA', 'UConn'],
          r2: ['Duke', "St. John's", 'Michigan State', 'UConn'],
          s16: ['Michigan State', 'UConn'],
          e8: ['Michigan State']
        },
        west: {
          r1: ['Arizona', 'Villanova', 'Wisconsin', 'Arkansas', 'BYU', 'Gonzaga', 'Miami (FL)', 'Purdue'],
          r2: ['Arizona', 'Arkansas', 'BYU', 'Purdue'],
          s16: ['Arizona', 'Purdue'],
          e8: ['Arizona']
        },
        midwest: {
          r1: ['Michigan', 'Georgia', 'Texas Tech', 'Alabama', 'Tennessee', 'Virginia', 'Kentucky', 'Iowa State'],
          r2: ['Michigan', 'Alabama', 'Tennessee', 'Iowa State'],
          s16: ['Michigan', 'Iowa State'],
          e8: ['Michigan']
        },
        south: {
          r1: ['Florida', 'Iowa', 'Vanderbilt', 'Nebraska', 'VCU', 'Illinois', 'Texas A&M', 'Houston'],
          r2: ['Florida', 'Vanderbilt', 'Illinois', 'Houston'],
          s16: ['Florida', 'Houston'],
          e8: ['Houston']
        }
      },
      finalFour: {
        semi1: { teams: ['Michigan State', 'Arizona'], winner: 'Arizona' },
        semi2: { teams: ['Michigan', 'Houston'], winner: 'Arizona' },
        champion: 'Arizona'
      }
    }
  ];

  // Fix finalFour semi2 winners (they should be the winner of semi2, not the champion)
  BRACKETS[0].finalFour.semi2.winner = 'Michigan';
  BRACKETS[3].finalFour.semi2.winner = 'Michigan';

  /* ---- KenPom / Odds Data for Analysis Section ---- */
  const ANALYTICS = [
    { team: 'Duke', kenpom: 1, offEff: 4, defEff: 2, odds: '+300', oddsNum: 300, expertPct: 15, publicEst: 18 },
    { team: 'Michigan', kenpom: 2, offEff: 8, defEff: 1, odds: '+370', oddsNum: 370, expertPct: 17, publicEst: 15 },
    { team: 'Arizona', kenpom: 3, offEff: 5, defEff: 3, odds: '+380', oddsNum: 380, expertPct: 55, publicEst: 20 },
    { team: 'Florida', kenpom: 4, offEff: 9, defEff: 6, odds: '+750', oddsNum: 750, expertPct: 8, publicEst: 12 },
    { team: 'Houston', kenpom: 5, offEff: 14, defEff: 5, odds: '13-1', oddsNum: 1300, expertPct: 2, publicEst: 5 },
    { team: 'Iowa State', kenpom: 6, offEff: 21, defEff: 4, odds: '18-1', oddsNum: 1800, expertPct: 0, publicEst: 2 },
    { team: 'UConn', kenpom: 7, offEff: 28, defEff: 11, odds: '20-1', oddsNum: 2000, expertPct: 12, publicEst: 6 },
    { team: 'Michigan State', kenpom: 8, offEff: 15, defEff: 9, odds: '22-1', oddsNum: 2200, expertPct: 12, publicEst: 4 },
    { team: 'Illinois', kenpom: 9, offEff: 7, defEff: 14, odds: '22-1', oddsNum: 2200, expertPct: 0, publicEst: 3 },
    { team: 'Purdue', kenpom: 10, offEff: 10, defEff: 12, odds: '25-1', oddsNum: 2500, expertPct: 0, publicEst: 3 }
  ];

  /* ---- Dark Mode ---- */
  function initTheme() {
    var saved = localStorage.getItem('mm-theme');
    if (saved) {
      document.documentElement.setAttribute('data-theme', saved);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
    updateThemeIcon();
  }

  function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('mm-theme', next);
    updateThemeIcon();
  }

  function updateThemeIcon() {
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    btn.textContent = isDark ? 'Light Mode' : 'Dark Mode';
  }

  /* ---- Scroll Reveal ---- */
  function initReveal() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('.reveal').forEach(function (el) {
        el.classList.add('visible');
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.reveal').forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ---- Bracket Card Toggle ---- */
  function initBracketCards() {
    document.querySelectorAll('.bracket-card__header').forEach(function (header) {
      header.addEventListener('click', function () {
        var card = header.closest('.bracket-card');
        card.classList.toggle('is-open');
      });
    });
  }

  /* ---- Region Tabs ---- */
  function initRegionTabs() {
    document.querySelectorAll('.region-tabs').forEach(function (tabBar) {
      var tabs = tabBar.querySelectorAll('.region-tab');
      var card = tabBar.closest('.bracket-card__content');
      var regions = card.querySelectorAll('.bracket-region');

      tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
          tabs.forEach(function (t) { t.classList.remove('is-active'); });
          regions.forEach(function (r) { r.classList.remove('is-active'); });

          tab.classList.add('is-active');
          var target = card.querySelector('[data-region="' + tab.dataset.region + '"]');
          if (target) target.classList.add('is-active');
        });
      });
    });
  }

  /* ---- Render Bracket Picks for a Region ---- */
  function renderRegionBracket(bracketData, regionKey) {
    var region = REGIONS[regionKey];
    var picks = bracketData.regions[regionKey];
    var html = '<div class="bracket-rounds">';

    // Round of 64: 8 matchups
    html += '<div class="bracket-round"><div class="bracket-round__title">Rd of 64</div>';
    for (var i = 0; i < 8; i++) {
      var t1 = region.teams[i * 2];
      var t2 = region.teams[i * 2 + 1];
      var winner = picks.r1[i];
      var isUpset = false;
      if (winner === t2.name && t2.seed > t1.seed) isUpset = true;
      if (winner === t1.name && t1.seed > t2.seed) isUpset = true;

      html += '<div class="bracket-matchup">';
      html += renderTeamLine(t1, winner === t1.name, isUpset && winner === t1.name);
      html += renderTeamLine(t2, winner === t2.name, isUpset && winner === t2.name);
      html += '</div>';
    }
    html += '</div>';

    // Round of 32: 4 matchups
    html += '<div class="bracket-round"><div class="bracket-round__title">Rd of 32</div>';
    for (var j = 0; j < 4; j++) {
      var team1Name = picks.r1[j * 2];
      var team2Name = picks.r1[j * 2 + 1];
      var r2Winner = picks.r2[j];
      var team1 = findTeam(region, team1Name);
      var team2 = findTeam(region, team2Name);
      var r2Upset = team1 && team2 && r2Winner === team2.name && team2.seed > team1.seed;
      if (team1 && team2 && r2Winner === team1.name && team1.seed > team2.seed) r2Upset = true;

      html += '<div class="bracket-matchup">';
      html += renderTeamLine(team1, r2Winner === team1.name, r2Upset && r2Winner === team1.name);
      html += renderTeamLine(team2, r2Winner === team2.name, r2Upset && r2Winner === team2.name);
      html += '</div>';
    }
    html += '</div>';

    // Sweet 16: 2 matchups
    html += '<div class="bracket-round"><div class="bracket-round__title">Sweet 16</div>';
    for (var k = 0; k < 2; k++) {
      var s1Name = picks.r2[k * 2];
      var s2Name = picks.r2[k * 2 + 1];
      var s16Winner = picks.s16[k];
      var s1 = findTeam(region, s1Name);
      var s2 = findTeam(region, s2Name);
      var s16Upset = s1 && s2 && s16Winner === s2.name && s2.seed > s1.seed;
      if (s1 && s2 && s16Winner === s1.name && s1.seed > s2.seed) s16Upset = true;

      html += '<div class="bracket-matchup">';
      html += renderTeamLine(s1, s16Winner === s1.name, s16Upset && s16Winner === s1.name);
      html += renderTeamLine(s2, s16Winner === s2.name, s16Upset && s16Winner === s2.name);
      html += '</div>';
    }
    html += '</div>';

    // Elite 8: 1 matchup
    html += '<div class="bracket-round"><div class="bracket-round__title">Elite 8</div>';
    var e1Name = picks.s16[0];
    var e2Name = picks.s16[1];
    var e8Winner = picks.e8[0];
    var e1 = findTeam(region, e1Name);
    var e2 = findTeam(region, e2Name);
    var e8Upset = e1 && e2 && e8Winner === e2.name && e2.seed > e1.seed;
    if (e1 && e2 && e8Winner === e1.name && e1.seed > e2.seed) e8Upset = true;

    html += '<div class="bracket-matchup">';
    html += renderTeamLine(e1, e8Winner === e1.name, e8Upset && e8Winner === e1.name);
    html += renderTeamLine(e2, e8Winner === e2.name, e8Upset && e8Winner === e2.name);
    html += '</div>';
    html += '</div>';

    html += '</div>'; // close bracket-rounds
    return html;
  }

  function findTeam(region, name) {
    if (!name) return { seed: 0, name: '?' };
    for (var i = 0; i < region.teams.length; i++) {
      if (region.teams[i].name === name) return region.teams[i];
    }
    return { seed: 0, name: name };
  }

  function renderTeamLine(team, isWinner, isUpset) {
    if (!team) return '';
    var cls = 'bracket-team seed-' + team.seed;
    if (isWinner) cls += ' is-winner';
    if (isUpset) cls += ' is-upset';
    return '<div class="' + cls + '">' +
      '<span class="bracket-team__seed">' + team.seed + '</span>' +
      '<span class="bracket-team__name">' + team.name + '</span>' +
      '</div>';
  }

  /* ---- Render Final Four ---- */
  function renderFinalFour(bracket) {
    var ff = bracket.finalFour;
    var html = '<div class="final-four-grid">';

    // Semi 1
    html += '<div class="ff-semifinal">';
    html += '<div class="ff-team' + (ff.semi1.winner === ff.semi1.teams[0] ? ' is-winner' : '') + '">' + ff.semi1.teams[0] + '</div>';
    html += '<div style="font-size:var(--text-xs);color:var(--text-tertiary);margin:4px 0;">vs</div>';
    html += '<div class="ff-team' + (ff.semi1.winner === ff.semi1.teams[1] ? ' is-winner' : '') + '">' + ff.semi1.teams[1] + '</div>';
    html += '</div>';

    // Champion
    html += '<div class="ff-champion">';
    html += '<div class="ff-champion__label">Champion</div>';
    html += '<div class="ff-champion__team">' + bracket.champion + '</div>';
    html += '</div>';

    // Semi 2
    html += '<div class="ff-semifinal">';
    html += '<div class="ff-team' + (ff.semi2.winner === ff.semi2.teams[0] ? ' is-winner' : '') + '">' + ff.semi2.teams[0] + '</div>';
    html += '<div style="font-size:var(--text-xs);color:var(--text-tertiary);margin:4px 0;">vs</div>';
    html += '<div class="ff-team' + (ff.semi2.winner === ff.semi2.teams[1] ? ' is-winner' : '') + '">' + ff.semi2.teams[1] + '</div>';
    html += '</div>';

    html += '</div>';
    return html;
  }

  /* ---- Build All Bracket Cards ---- */
  function buildBracketCards() {
    var container = document.getElementById('brackets-container');
    if (!container) return;

    var regionKeys = ['east', 'west', 'midwest', 'south'];

    BRACKETS.forEach(function (bracket) {
      var card = document.createElement('div');
      card.className = 'bracket-card reveal';

      // Header
      var headerHTML = '<div class="bracket-card__header">' +
        '<div class="bracket-card__meta">' +
        '<div class="bracket-card__number">' + bracket.id + '</div>' +
        '<div class="bracket-card__info">' +
        '<h3>' + bracket.name + '</h3>' +
        '<div class="bracket-card__subtitle">' + bracket.subtitle + '</div>' +
        '</div></div>' +
        '<div class="bracket-card__champion"><span class="trophy">&#127942;</span> ' + bracket.champion + '</div>' +
        '<div class="bracket-card__toggle"><svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg></div>' +
        '</div>';

      // Body
      var bodyHTML = '<div class="bracket-card__body"><div class="bracket-card__content">';

      // Strategy text
      bodyHTML += '<div class="strategy-text"><p>' + bracket.strategy + '</p></div>';

      // Final Four visualization
      bodyHTML += '<h4>Final Four</h4>';
      bodyHTML += renderFinalFour(bracket);

      // Region tabs
      bodyHTML += '<div class="region-tabs">';
      regionKeys.forEach(function (key, idx) {
        bodyHTML += '<button class="region-tab' + (idx === 0 ? ' is-active' : '') + '" data-region="' + key + '">' + REGIONS[key].name + '</button>';
      });
      bodyHTML += '</div>';

      // Region bracket displays
      regionKeys.forEach(function (key, idx) {
        bodyHTML += '<div class="bracket-region' + (idx === 0 ? ' is-active' : '') + '" data-region="' + key + '">';
        bodyHTML += renderRegionBracket(bracket, key);
        bodyHTML += '</div>';
      });

      bodyHTML += '</div></div>';
      card.innerHTML = headerHTML + bodyHTML;
      container.appendChild(card);
    });
  }

  /* ---- Build Analytics Charts ---- */
  function buildAnalytics() {
    var kenpomChart = document.getElementById('kenpom-chart');
    var oddsChart = document.getElementById('odds-chart');
    var leverageChart = document.getElementById('leverage-chart');

    if (kenpomChart) {
      var maxKenpom = 10;
      var html = '<div class="bar-chart">';
      ANALYTICS.slice(0, 8).forEach(function (t) {
        var width = Math.max(10, ((maxKenpom - t.kenpom + 1) / maxKenpom) * 100);
        html += '<div class="bar-row">' +
          '<span class="bar-label">' + t.team + '</span>' +
          '<div class="bar-track"><div class="bar-fill bar-fill--blue" style="width:' + width + '%">' +
          '<span class="bar-value">#' + t.kenpom + '</span></div></div></div>';
      });
      html += '</div>';
      kenpomChart.innerHTML = html;
    }

    if (oddsChart) {
      var html2 = '<div class="bar-chart">';
      ANALYTICS.slice(0, 8).forEach(function (t) {
        var impliedPct;
        if (t.oddsNum <= 1000) {
          impliedPct = (100 / (t.oddsNum / 100 + 1)).toFixed(1);
        } else {
          impliedPct = (100 / (t.oddsNum / 100 + 1)).toFixed(1);
        }
        var width = Math.max(8, parseFloat(impliedPct) * 3);
        html2 += '<div class="bar-row">' +
          '<span class="bar-label">' + t.team + '</span>' +
          '<div class="bar-track"><div class="bar-fill bar-fill--amber" style="width:' + width + '%">' +
          '<span class="bar-value">' + t.odds + ' (' + impliedPct + '%)</span></div></div></div>';
      });
      html2 += '</div>';
      oddsChart.innerHTML = html2;
    }

    if (leverageChart) {
      var html3 = '<div class="bar-chart">';
      // Leverage = implied win% - estimated public pick%
      // Positive = underselected by public (good value)
      var leverageData = ANALYTICS.map(function (t) {
        var impliedPct = 100 / (t.oddsNum / 100 + 1);
        var leverage = impliedPct - t.publicEst;
        return { team: t.team, leverage: leverage, impliedPct: impliedPct, publicEst: t.publicEst };
      }).sort(function (a, b) { return b.leverage - a.leverage; });

      leverageData.forEach(function (t) {
        var isPositive = t.leverage > 0;
        var width = Math.max(8, Math.abs(t.leverage) * 6);
        var cls = isPositive ? 'bar-fill--green' : 'bar-fill';
        var sign = t.leverage > 0 ? '+' : '';
        html3 += '<div class="bar-row">' +
          '<span class="bar-label">' + t.team + '</span>' +
          '<div class="bar-track"><div class="bar-fill ' + cls + '" style="width:' + width + '%">' +
          '<span class="bar-value">' + sign + t.leverage.toFixed(1) + '%</span></div></div></div>';
      });
      html3 += '</div>';
      leverageChart.innerHTML = html3;
    }
  }

  /* ---- Initialize ---- */
  function init() {
    initTheme();
    buildBracketCards();
    buildAnalytics();
    initBracketCards();
    initRegionTabs();
    initReveal();

    var toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) toggleBtn.addEventListener('click', toggleTheme);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
