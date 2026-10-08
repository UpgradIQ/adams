# Template Catalog

This catalog defines the canonical section structures for 230 startup innovation tools.
When the user requests a template by name, use the matching entry as the starting
specification. You may improve naming and order, but preserve the core sections.

Each entry follows this format:
- **Name**: the template title
- **Type**: worksheet, canvas, matrix, planner, scorecard, assessment, mapping_tool, framework, calculator
- **Sections**: the section IDs, titles, span, and rows. Span defaults to `full` if not listed.
- **Flow**: the logical thinking sequence

Templates are organized by domain. Use the domain as the default section group name
when the user requests a template from a domain with more than 10 sections.

---

## 1. Business Model and Venture Design

### Business Model Canvas
- Type: canvas
- Flow: Segments > Value > Channels > Relationships > Revenue > Resources > Activities > Partners > Costs
- Sections:
  1. customer-segments | Customer Segments | half | 5
  2. value-propositions | Value Propositions | half | 5
  3. channels | Channels | third | 4
  4. customer-relationships | Customer Relationships | third | 4
  5. revenue-streams | Revenue Streams | third | 4
  6. key-resources | Key Resources | third | 4
  7. key-activities | Key Activities | third | 4
  8. key-partnerships | Key Partnerships | third | 4
  9. cost-structure | Cost Structure | full | 4

### Lean Canvas
- Type: canvas
- Flow: Problem > Segments > UVP > Solution > Channels > Revenue > Costs > Metrics > Advantage
- Sections:
  1. problem | Problem | half | 4
  2. customer-segments | Customer Segments | half | 4
  3. unique-value-proposition | Unique Value Proposition | full | 3
  4. solution | Solution | half | 4
  5. channels | Channels | half | 4
  6. revenue-streams | Revenue Streams | half | 3
  7. cost-structure | Cost Structure | half | 3
  8. key-metrics | Key Metrics | half | 3
  9. unfair-advantage | Unfair Advantage | half | 3

### Value Proposition Canvas
- Type: canvas
- Flow: Customer Profile > Jobs > Pains > Gains > Products > Pain Relievers > Gain Creators
- Sections:
  1. customer-jobs | Customer Jobs | half | 5
  2. customer-pains | Customer Pains | half | 5
  3. customer-gains | Customer Gains | half | 5
  4. products-services | Products and Services | half | 5
  5. pain-relievers | Pain Relievers | half | 5
  6. gain-creators | Gain Creators | half | 5

### Mission Model Canvas
- Type: canvas
- Flow: same as Business Model Canvas but with Mission instead of Revenue
- Sections: same as Business Model Canvas, replacing revenue-streams with mission-achievement | Mission Achievement | third | 4

### Platform Business Model Canvas
- Type: canvas
- Flow: Producers > Consumers > Platform Value > Core Interaction > Channels > Revenue > Costs
- Sections:
  1. producers | Producers | half | 4
  2. consumers | Consumers | half | 4
  3. platform-value | Platform Value Unit | full | 3
  4. core-interaction | Core Interaction | half | 4
  5. channels | Channels | half | 4
  6. revenue-model | Revenue Model | half | 3
  7. cost-structure | Cost Structure | half | 3
  8. network-effects | Network Effects | full | 4

### Revenue Model Canvas
- Type: canvas
- Flow: Segments > Value Delivered > Pricing Logic > Payment Model > Revenue Math
- Sections:
  1. target-segments | Target Segments | half | 4
  2. value-delivered | Value Delivered | half | 4
  3. pricing-logic | Pricing Logic | half | 4
  4. payment-model | Payment Model | half | 4
  5. revenue-math | Revenue Calculation | full | 4

### Pricing Strategy Canvas
- Type: canvas
- Flow: Value Perception > Competitor Pricing > Cost Floor > Pricing Model > Price Points > Testing
- Sections:
  1. value-perception | Value Perception | half | 4
  2. competitor-pricing | Competitor Benchmarks | half | 4
  3. cost-floor | Cost Floor | half | 3
  4. pricing-model | Pricing Model | half | 3
  5. price-points | Proposed Price Points | half | 4
  6. testing-plan | Pricing Test Plan | half | 4

### Business Assumptions Canvas
- Type: canvas
- Flow: Customer Assumptions > Problem Assumptions > Solution Assumptions > Business Assumptions > Ranking
- Sections:
  1. customer-assumptions | Customer Assumptions | half | 5
  2. problem-assumptions | Problem Assumptions | half | 5
  3. solution-assumptions | Solution Assumptions | half | 5
  4. business-assumptions | Business Model Assumptions | half | 5
  5. assumption-ranking | Risk-Ranked Assumptions | full | 4

---

## 2. Customer, Problem, and Market Discovery

### Customer Segment Profile
- Type: worksheet
- Sections:
  1. segment-name | Segment Name | full | input
  2. demographics | Demographics | half | 4
  3. psychographics | Psychographics | half | 4
  4. behaviors | Behaviors and Habits | half | 4
  5. needs | Needs and Goals | half | 4
  6. pain-points | Pain Points | full | 5
  7. current-solutions | Current Solutions | full | 4

### Empathy Map
- Type: canvas
- Sections:
  1. think-feel | Think and Feel | half | 4
  2. see | See | half | 4
  3. hear | Hear | half | 4
  4. say-do | Say and Do | half | 4
  5. pains | Pains | half | 5
  6. gains | Gains | half | 5

### Jobs to Be Done Framework
- Type: framework
- Sections:
  1. job-statement | Job Statement | full | 3
  2. functional-job | Functional Job | half | 4
  3. emotional-job | Emotional Job | half | 4
  4. social-job | Social Job | half | 4
  5. related-jobs | Related Jobs | half | 4
  6. current-solution | Current Solution | full | 4
  7. desired-outcome | Desired Outcome | full | 4

### Problem-Solution Fit Canvas
- Type: canvas
- Sections:
  1. target-customer | Target Customer | half | 4
  2. problem-statement | Problem Statement | half | 5
  3. existing-alternatives | Existing Alternatives | half | 4
  4. proposed-solution | Proposed Solution | half | 5
  5. unique-value | Unique Value | full | 3
  6. evidence | Evidence of Fit | full | 4

### Customer Journey Map
- Type: mapping_tool
- Sections:
  1. awareness | Awareness Stage | half | 4
  2. consideration | Consideration Stage | half | 4
  3. decision | Decision Stage | half | 4
  4. onboarding | Onboarding Stage | half | 4
  5. retention | Retention Stage | half | 4
  6. advocacy | Advocacy Stage | half | 4
  7. pain-points | Pain Points Across Journey | full | 5
  8. opportunities | Improvement Opportunities | full | 5

---

## 3. Idea Generation and Innovation Strategy

### Opportunity Solution Tree
- Type: framework
- Sections:
  1. desired-outcome | Desired Outcome | full | 3
  2. opportunities | Opportunities | full | 5
  3. solutions | Solutions | full | 5
  4. experiments | Experiments | full | 5

### Innovation Ambition Matrix
- Type: matrix
- Sections:
  1. core-innovation | Core Innovation (70%) | third | 5
  2. adjacent-innovation | Adjacent Innovation (20%) | third | 5
  3. transformational-innovation | Transformational Innovation (10%) | third | 5
  4. resource-allocation | Resource Allocation | full | 4
  5. risk-assessment | Risk Assessment | full | 4

### Idea Prioritisation Matrix
- Type: matrix
- Sections:
  1. high-impact-low-effort | High Impact, Low Effort | half | 5
  2. high-impact-high-effort | High Impact, High Effort | half | 5
  3. low-impact-low-effort | Low Impact, Low Effort | half | 4
  4. low-impact-high-effort | Low Impact, High Effort | half | 4
  5. decision | Prioritisation Decision | full | 4

### Opportunity Canvas
- Type: canvas
- Sections:
  1. problem-or-need | Problem or Need | half | 4
  2. target-market | Target Market | half | 4
  3. market-size | Market Size Estimate | half | 4
  4. competitive-landscape | Competitive Landscape | half | 4
  5. solution-concept | Solution Concept | full | 5
  6. differentiation | Differentiation | full | 4
  7. feasibility | Feasibility Assessment | full | 4

---

## 4. Product, MVP, and Experimentation

### MVP Canvas
- Type: canvas
- Sections:
  1. hypothesis | Core Hypothesis | full | 3
  2. target-user | Target User | half | 4
  3. problem | Problem to Solve | half | 4
  4. mvp-features | MVP Feature Set | full | 5
  5. success-metrics | Success Metrics | half | 4
  6. learning-goals | Learning Goals | half | 4
  7. timeline | Build Timeline | full | 3

### Experiment Design Canvas
- Type: canvas
- Sections:
  1. hypothesis | Hypothesis | full | 3
  2. riskiest-assumption | Riskiest Assumption | full | 3
  3. experiment-type | Experiment Type | half | 3
  4. audience | Test Audience | half | 3
  5. success-criteria | Success Criteria | half | 4
  6. failure-criteria | Failure Criteria | half | 4
  7. method | Method and Steps | full | 5
  8. results | Results and Learning | full | 5

### Assumption Mapping
- Type: mapping_tool
- Sections:
  1. desirability | Desirability Assumptions | half | 5
  2. feasibility | Feasibility Assumptions | half | 5
  3. viability | Viability Assumptions | half | 5
  4. usability | Usability Assumptions | half | 5
  5. risk-ranking | Risk Ranking | full | 4
  6. test-plan | Test Plan for Top 3 | full | 5

### North Star Metric Framework
- Type: framework
- Sections:
  1. north-star | North Star Metric | full | 3
  2. input-metrics | Input Metrics | full | 5
  3. customer-value | How It Reflects Customer Value | full | 4
  4. revenue-connection | How It Connects to Revenue | full | 4
  5. measurement-plan | Measurement Plan | full | 4

### Pirate Metrics AARRR
- Type: framework
- Sections:
  1. acquisition | Acquisition | full | 4
  2. activation | Activation | full | 4
  3. retention | Retention | full | 4
  4. revenue | Revenue | full | 4
  5. referral | Referral | full | 4
  6. focus-metric | Current Focus Metric | full | 3

---

## 5. Product Strategy and Execution

### Product Vision Board
- Type: canvas
- Sections:
  1. vision | Vision | full | 3
  2. target-group | Target Group | half | 4
  3. needs | Needs | half | 4
  4. product | Product | half | 4
  5. business-goals | Business Goals | half | 4
  6. differentiators | Differentiators | full | 4

### Product-Market Fit Canvas
- Type: canvas
- Sections:
  1. target-customer | Target Customer | half | 4
  2. underserved-needs | Underserved Needs | half | 5
  3. value-proposition | Value Proposition | full | 4
  4. feature-set | Feature Set | half | 5
  5. competitive-advantage | Competitive Advantage | half | 4
  6. distribution-channel | Distribution Channel | half | 4
  7. revenue-model | Revenue Model | half | 4
  8. fit-evidence | Evidence of Fit | full | 5

### Product Roadmap Canvas
- Type: planner
- Sections:
  1. vision | Product Vision | full | 3
  2. now | Now (Current Quarter) | third | 5
  3. next | Next (Next Quarter) | third | 5
  4. later | Later (6+ Months) | third | 5
  5. metrics | Success Metrics | full | 4
  6. risks | Risks and Dependencies | full | 4

---

## 6. Go-to-Market, Sales, and Growth

### Go-to-Market Canvas
- Type: canvas
- Sections:
  1. target-market | Target Market | half | 4
  2. value-proposition | Value Proposition | half | 4
  3. channels | Distribution Channels | half | 4
  4. messaging | Key Messaging | half | 4
  5. pricing | Pricing Strategy | half | 4
  6. sales-motion | Sales Motion | half | 4
  7. launch-plan | Launch Plan | full | 5
  8. success-metrics | Success Metrics | full | 4

### Positioning Canvas
- Type: canvas
- Sections:
  1. target-audience | Target Audience | half | 4
  2. market-category | Market Category | half | 3
  3. competitive-alternatives | Competitive Alternatives | half | 4
  4. unique-differentiation | Unique Differentiation | half | 4
  5. key-benefit | Key Benefit | full | 3
  6. proof-points | Proof Points | full | 4
  7. positioning-statement | Positioning Statement | full | 4

### Growth Loops Canvas
- Type: canvas
- Sections:
  1. trigger | Trigger | half | 4
  2. action | User Action | half | 4
  3. output | Output | half | 4
  4. reinvestment | Reinvestment Mechanism | half | 4
  5. loop-metrics | Loop Metrics | full | 4
  6. bottlenecks | Bottlenecks and Levers | full | 4

---

## 7. Finance, Valuation, and Unit Economics

### Unit Economics Worksheet
- Type: worksheet
- Sections:
  1. revenue-per-unit | Revenue per Unit | half | 3
  2. cogs-per-unit | Cost of Goods per Unit | half | 3
  3. gross-margin | Gross Margin | half | 3
  4. cac | Customer Acquisition Cost | half | 3
  5. ltv | Lifetime Value | half | 3
  6. ltv-cac-ratio | LTV to CAC Ratio | half | 3
  7. payback-period | Payback Period | full | 3
  8. unit-economics-summary | Summary and Implications | full | 5

### Burn Rate Calculator
- Type: calculator
- Sections:
  1. monthly-revenue | Monthly Revenue | half | 3
  2. monthly-expenses | Monthly Expenses | half | 3
  3. monthly-burn | Monthly Net Burn | half | 3
  4. cash-on-hand | Cash on Hand | half | 3
  5. runway-months | Runway in Months | full | 3
  6. actions-to-extend | Actions to Extend Runway | full | 5

### Valuation Worksheet
- Type: worksheet
- Sections:
  1. revenue-metrics | Revenue and Growth Metrics | half | 4
  2. market-size | Total Addressable Market | half | 4
  3. comparable-companies | Comparable Company Multiples | full | 5
  4. dcf-assumptions | DCF Assumptions | half | 4
  5. scorecard-method | Scorecard Method | half | 4
  6. valuation-range | Valuation Range Summary | full | 4
  7. negotiation-notes | Negotiation Notes | full | 4

### Scenario Planning Model
- Type: worksheet
- Sections:
  1. base-case | Base Case | third | 5
  2. best-case | Best Case | third | 5
  3. worst-case | Worst Case | third | 5
  4. key-variables | Key Variables | full | 4
  5. trigger-points | Trigger Points | full | 4
  6. contingency-actions | Contingency Actions | full | 5

---

## 8. Fundraising and Investor Readiness

### Investor Narrative Canvas
- Type: canvas
- Sections:
  1. problem | Problem | full | 4
  2. market-opportunity | Market Opportunity | half | 4
  3. solution | Solution | half | 4
  4. traction | Traction | half | 4
  5. business-model | Business Model | half | 4
  6. team | Team | half | 4
  7. competitive-moat | Competitive Moat | half | 4
  8. ask | The Ask | full | 3
  9. use-of-funds | Use of Funds | full | 4

### Fundraising Strategy Canvas
- Type: canvas
- Sections:
  1. funding-goal | Funding Goal | half | 3
  2. current-stage | Current Stage | half | 3
  3. milestone-targets | Milestones This Round Enables | full | 5
  4. investor-profile | Target Investor Profile | half | 4
  5. outreach-strategy | Outreach Strategy | half | 4
  6. timeline | Fundraising Timeline | full | 4
  7. terms-expectations | Expected Terms | full | 4

### KPI Scorecard
- Type: scorecard
- Sections:
  1. north-star | North Star Metric | full | 3
  2. growth-kpis | Growth KPIs | half | 5
  3. engagement-kpis | Engagement KPIs | half | 5
  4. revenue-kpis | Revenue KPIs | half | 5
  5. efficiency-kpis | Efficiency KPIs | half | 5
  6. commentary | Period Commentary | full | 5

---

## 9. Team, Operations, and Organizational Design

### Operating Model Canvas
- Type: canvas
- Sections:
  1. strategy | Strategy | full | 4
  2. processes | Core Processes | half | 5
  3. people | People and Capabilities | half | 5
  4. technology | Technology | half | 4
  5. governance | Governance | half | 4
  6. metrics | Operating Metrics | full | 4

### OKR Framework
- Type: framework
- Sections:
  1. objective | Objective | full | 3
  2. key-result-1 | Key Result 1 | full | 3
  3. key-result-2 | Key Result 2 | full | 3
  4. key-result-3 | Key Result 3 | full | 3
  5. initiatives | Initiatives | full | 5
  6. risks | Risks and Dependencies | full | 4

### RACI Matrix
- Type: matrix
- Sections:
  1. responsible | Responsible | half | 5
  2. accountable | Accountable | half | 5
  3. consulted | Consulted | half | 5
  4. informed | Informed | half | 5
  5. decision-context | Decision Context | full | 4

---

## 10. Risk, Compliance, and Resilience

### SWOT Analysis
- Type: matrix
- Sections:
  1. strengths | Strengths | half | 5
  2. weaknesses | Weaknesses | half | 5
  3. opportunities | Opportunities | half | 5
  4. threats | Threats | half | 5
  5. strategic-implications | Strategic Implications | full | 5

### Risk Register
- Type: worksheet
- Sections:
  1. risk-description | Risk Description | full | 4
  2. likelihood | Likelihood (1 to 5) | half | 3
  3. impact | Impact (1 to 5) | half | 3
  4. risk-score | Risk Score | half | 3
  5. mitigation-strategy | Mitigation Strategy | half | 5
  6. owner | Risk Owner | half | input
  7. review-date | Review Date | half | input

### Pre-Mortem Workshop
- Type: worksheet
- Sections:
  1. project-description | Project Description | full | 4
  2. failure-scenario | Imagine It Failed: What Happened? | full | 5
  3. root-causes | Most Likely Root Causes | full | 5
  4. early-warnings | Early Warning Signs | full | 4
  5. preventive-actions | Preventive Actions | full | 5

---

## 11. Partnerships and Ecosystem

### Partner Ecosystem Map
- Type: mapping_tool
- Sections:
  1. core-partners | Core Partners | half | 5
  2. strategic-partners | Strategic Partners | half | 5
  3. value-exchange | Value Exchange | full | 5
  4. dependencies | Dependencies | full | 4
  5. partnership-risks | Partnership Risks | full | 4

---

## 12. Sustainability and Impact

### Theory of Change
- Type: framework
- Sections:
  1. long-term-impact | Long-Term Impact | full | 4
  2. outcomes | Outcomes | full | 5
  3. outputs | Outputs | full | 5
  4. activities | Activities | full | 5
  5. inputs | Inputs and Resources | full | 4
  6. assumptions | Assumptions | full | 4

### Impact Model Canvas
- Type: canvas
- Sections:
  1. problem | Problem | half | 4
  2. beneficiaries | Beneficiaries | half | 4
  3. activities | Activities | half | 4
  4. outputs | Outputs | half | 4
  5. outcomes | Outcomes | full | 5
  6. impact-metrics | Impact Metrics | full | 4
  7. sustainability | Financial Sustainability | full | 4

---

## Lookup Instructions

When the user requests a template by name:

1. Search this catalog for a matching or closely matching name.
2. If found, use the catalog entry as the base specification.
3. Apply the user's customizations on top (audience, stage, extra sections).
4. Generate helper content specific to the template's domain.
5. If not found, derive the specification from domain knowledge using the nearest
   catalog entry in the same domain as a structural reference.

When the user requests a template from a domain not covered here, use the layout
heuristics from SKILL.md and the structural patterns from spec-contract.md to build
a high-quality specification from scratch.
