export const PORTFOLIO_DATA = {
  assets: {
    "MSFT": { id: "MSFT", name: "Microsoft Corporation", price: 358.00, pe: 21, mcap: "$2.77T", revGrowth: "+17%", target: 597, upside: 67, signal: "Strong Buy", action: "Add", color: "blue", insights: "AI infrastructure leader. Azure + Copilot monetization." },
    "NVDA": { id: "NVDA", name: "NVIDIA Corporation", price: 171.00, pe: 37, mcap: "$4.69T", revGrowth: "+65%", target: 266, upside: 55, signal: "Strong Buy", action: "Add", color: "green", insights: "AI compute monopoly. Blackwell ramp sustaining growth." },
    "META": { id: "META", name: "Meta Platforms, Inc.", price: 529.00, pe: 18.73, mcap: "$1.39T", revGrowth: "+24%", target: 841, upside: 59, signal: "Strong Buy", action: "Add", color: "blue", insights: "52-wk low. Ad machine + Llama 4 live. Max fear = max opportunity." },
    "BROS": { id: "BROS", name: "Dutch Bros Inc.", price: 51.00, pe: 59, mcap: "$8.3B", revGrowth: "+28%", target: 77, upside: 51, signal: "Strong Buy", action: "Initiate", color: "purple", insights: "High-growth drive-thru coffee. National expansion ahead." },
    "AMZN": { id: "AMZN", name: "Amazon.com, Inc.", price: 208.00, pe: 29, mcap: "$2.2T", revGrowth: "+12%", target: 279, upside: 34, signal: "Strong Buy", action: "Hold", color: "blue", insights: "AWS re-accelerating. Retail margins expanding." },
    "GOOG": { id: "GOOG", name: "Alphabet Inc.", price: 285.00, pe: 25, mcap: "$2.1T", revGrowth: "+14%", target: 375, upside: 32, signal: "Buy", action: "Hold", color: "blue", insights: "Search + Cloud + YouTube. Gemini integration underway." },
    "MU": { id: "MU", name: "Micron Technology, Inc.", price: 363.87, pe: 16.78, mcap: "$410B", revGrowth: "+196%", target: 443, upside: 22, signal: "Strong Buy", action: "Add", color: "green", insights: "Cheapest growth in portfolio. HBM supercycle beneficiary." },
    "AAPL": { id: "AAPL", name: "Apple Inc.", price: 248.00, pe: 32, mcap: "$3.77T", revGrowth: "~5%", target: 296, upside: 19, signal: "Buy", action: "Hold", color: "blue", insights: "iPhone cycle maturing. Services growth is the story." },
    "TSLA": { id: "TSLA", name: "Tesla, Inc.", price: 385.00, pe: 327, mcap: "$1.43T", revGrowth: "~0%", target: 400, upside: 4, signal: "Hold", action: "Monitor", color: "amber", insights: "Robotaxi investigation. Revenue flat. Valuation demands execution." }
  },
  
  deepDives: {
    "MU": {
      ticker: "MU",
      bluf: "Down ~23% from post-earnings highs | 6 straight down days. The selloff is a tug-of-war. HBM4 is in volume production AHEAD of schedule. At 6.4x forward earnings, this is a gift entry.",
      verdict: "Strong Buy on Weakness",
      confidence: 88,
      metrics: [
        { lbl: "Q2 Rev", val: "$23.86B" }, { lbl: "Rev YoY", val: "+196%" }, { lbl: "Q2 EPS", val: "$12.20" }, { lbl: "Q3 Guide", val: "$33.5B" }
      ],
      bull: [
        "HBM4 36GB in volume production AHEAD of schedule for NVIDIA Vera Rubin.",
        "Q3 guidance ($33.5B) exceeds prior full-year revenue in history.",
        "6.4x fwd P/E is the cheapest growth story in the S&P 500."
      ],
      bear: [
        "$25B+ annual capex creates execution risk if cycle turns.",
        "Tariff escalation on modules/SSDs compresses margins.",
        "Google TurboQuant AI memory compression could reduce intensity."
      ]
    },
    "META": {
      ticker: "META",
      bluf: "52-week low | Down ~26%. Two child safety verdicts, Beijing blocking $2B Manus AI acquisition. But the $201B ad machine is intact, Llama 4 is live. Max fear, max opportunity.",
      verdict: "Strong Buy",
      confidence: 82,
      metrics: [
        { lbl: "FY25 Rev", val: "$201B" }, { lbl: "Rev YoY", val: "+22%" }, { lbl: "Q4 Op Margin", val: "41%" }, { lbl: "Fwd P/E", val: "18.73x" }
      ],
      bull: [
        "$201B revenue base growing 22%+ with expanding margins.",
        "Liability settlements manageable vs $80B+ annual OCF.",
        "18.73x P/E with 59% analyst upside."
      ],
      bear: [
        "SEC filings reference tens of billions in child safety exposure.",
        "Reality Labs: cumulative $83.6B losses.",
        "$125B AI capex with uncertain ROI timeline."
      ]
    },
    "BROS": {
      ticker: "BROS",
      bluf: "New Position Evaluation | Near 52-week low. AUV of $2.1M beats Starbucks ($1.8M) with sub-12-month payback. Starter position scaling into pullbacks.",
      verdict: "Starter Position",
      confidence: 68,
      metrics: [
        { lbl: "FY25 Rev", val: "$1.64B" }, { lbl: "Rev YoY", val: "+28%" }, { lbl: "AUV", val: "$2.1M" }, { lbl: "Payback", val: "<12 mo" }
      ],
      bull: [
        "Best-in-class unit economics: $2.1M AUV, 31% shop margins.",
        "Food menu national rollout ahead.",
        "East Coast expansion ahead."
      ],
      bear: [
        "Forward P/E of 59x demands perfect execution.",
        "Consumer discretionary risk if macro turns."
      ]
    }
  },

  macro: [
    { label: "Iran Conflict", val: "Active", risk: "high" },
    { label: "VIX", val: "27.44", risk: "high" },
    { label: "S&P 500 YTD", val: "-5.8%", risk: "high" },
    { label: "NASDAQ YTD", val: "-8.1%", risk: "high" },
    { label: "Fed Funds Rate", val: "3.50-3.75%", risk: "medium" },
    { label: "WTI Crude", val: "$100+", risk: "high" },
    { label: "PCE Inflation", val: "2.7%", risk: "medium" },
    { label: "10Y Yield", val: "Elevated", risk: "medium" }
  ]
};
