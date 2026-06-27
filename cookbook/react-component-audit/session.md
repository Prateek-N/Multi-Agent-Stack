---
domain: product_design
phases: 0–5
task: React settings page UI/UX audit — B2B SaaS (React + TypeScript + Tailwind)
entry_type: cookbook
---

# Cookbook: React Settings Page UI/UX Audit

## 1. CLI Invocation

```bash
python generate_prompt.py \
  --domain product_design \
  --task "Audit the settings page of a B2B SaaS React app. \
Six sections: Profile, Security, Notifications, Billing, Team, Integrations. \
Users report the page is confusing; high bounce rate from Billing. \
Component tree has 3 levels of nested state. \
Deliver severity-rated UX findings and a proposed redesign structure." \
  --context "stack=React+TypeScript+Tailwind; user_segment=SMB admins (non-technical); \
current_nav=left sidebar tabs; state_management=local useState+prop-drilling; \
bounce_metric=62pct of users who land on Billing leave without action"
```

---

## 2. Generated Prompt Block

```
════════════════════════════════════════════════════════════
  AGENTS-MAKER  |  SESSION PROMPT
  Generated: 2026-06-27T09:14:02Z
════════════════════════════════════════════════════════════

## Project Context

  Domain      : product_design
  Stack       : React 18, TypeScript 5, Tailwind CSS 3
  User Segment: SMB admins (non-technical); primary task = manage org settings
  Repository  : (not provided — audit is documentation-only)

## Session State

  Phase       : 0  (Task Framing — INIT)
  Prior phases: none
  Artifacts   : none

## Task

  Conduct a comprehensive UX audit of the settings page of a B2B SaaS
  application. The page exposes six sections via a left sidebar tab
  navigation: Profile, Security, Notifications, Billing, Team,
  Integrations.

  Known signals:
    - Users self-report the page as "confusing" (NPS verbatims, n=47)
    - 62 % of users who navigate to Billing leave without completing
      any action (Mixpanel, 30-day window)
    - Component tree is 3 levels deep with prop-drilled state
    - No URL routing per section (single /settings route)

  Deliverables:
    1. Severity-rated findings table (CRITICAL / HIGH / MEDIUM / LOW)
    2. Proposed component hierarchy for redesigned settings page

## Domain & Routing

  Primary agent  : ux_agent
  Support agents : architect_agent, ui_agent, execution_agent, reviewer_agent
  Orchestrator   : orchestrator (phases 0 and 5)
  Phase sequence : 0 → 1 → 2 → 3 → 4 → 5

════════════════════════════════════════════════════════════
```

---

## 3. Phase Transcripts

---

### Phase 0 — Task Framing

**Agent:** `orchestrator`

Scoping the audit before routing to specialist agents.

**Key clarifications locked in:**

- **User segment confirmed:** SMB org admins, 1–50 seat accounts, low technical literacy. They reach Settings from the top-right avatar menu. Primary jobs-to-be-done: invite teammates, update billing card, toggle email digests.
- **Success metric baseline:** Billing section task-completion rate currently 38 %. Target: ≥ 75 % post-redesign.
- **Scope boundary:** Audit covers information architecture, navigation model, state visibility, and error handling. Does not cover backend API contracts or authentication flows.
- **Component inventory provided by eng team:**
  - `SettingsPage` (route shell)
    - `SettingsSidebar` (tab list)
    - `SettingsContent` (conditional render via index state)
      - `ProfileSection` → `AvatarUpload`, `ProfileForm`, `DangerZone`
      - `SecuritySection` → `PasswordForm`, `TwoFactorPanel`, `SessionList`
      - `NotificationsSection` → `ChannelToggles`, `DigestFrequency`, `AlertRules`
      - `BillingSection` → `PlanSummary`, `PaymentMethodForm`, `InvoiceTable`, `UsageMetrics`
      - `TeamSection` → `MemberTable`, `InviteForm`, `RoleEditor`
      - `IntegrationsSection` → `IntegrationCard` (×n), `OAuthConnectButton`, `WebhookForm`

**Routing decision:** Phase 1 → `ux_agent` for user journey mapping and pain point inventory.

---

> **[Companion]** Phase 0 complete. Orchestrator has locked scope, confirmed user segment (SMB admins), and catalogued the full component tree. The 62 % Billing bounce rate is the highest-priority signal. Routing to ux_agent for Phase 1.

---

### Phase 1 — Requirements

**Agent:** `ux_agent`

**User Journey Map — Settings Page (SMB Admin)**

| Step | User Goal | Current Path | Friction Point |
|------|-----------|-------------|----------------|
| 1 | Add a new team member | Settings → Team → InviteForm | Invite button is below the fold in MemberTable on 13" screens |
| 2 | Update credit card | Settings → Billing → PaymentMethodForm | PlanSummary expands an accordion; PaymentMethodForm is hidden beneath InvoiceTable (280 px of invoices first) |
| 3 | Disable marketing emails | Settings → Notifications → ChannelToggles | ChannelToggles mixes product alerts and marketing; no visual grouping |
| 4 | Enable 2FA | Settings → Security → TwoFactorPanel | Panel shows a spinner on load (fetches TOTP seed on mount even if 2FA already enabled) |
| 5 | Connect Slack | Settings → Integrations → OAuthConnectButton | 14 IntegrationCards render in a flat list; Slack requires scroll on 1080p |

**Pain Point Inventory**

1. **No deep-link URLs per section.** Browser back button exits Settings entirely. Users who navigate away mid-task lose their position. Affects all six sections.
2. **BillingSection content order.** `UsageMetrics` and `InvoiceTable` precede `PaymentMethodForm` in DOM order and visual hierarchy. The primary CTA (update card) is buried below secondary content (historical invoices).
3. **State loss on tab switch.** `ProfileForm` has unsaved changes; user clicks Security tab — form state is silently discarded. No dirty-state guard.
4. **Prop-drilling causes re-render storms.** `SettingsContent` passes `activeSection` and `setActiveSection` through three component layers. Any section-level state change re-renders the entire page subtree.
5. **Cognitive overload in NotificationsSection.** 22 individual toggles with no grouping. Users cannot determine what "Alert Rules" affects without reading tooltip text.
6. **DangerZone proximity.** `DangerZone` (delete account) is a child of `ProfileSection` — visually adjacent to avatar upload. No visual separation or confirmation gate beyond a single modal.
7. **IntegrationsSection discoverability.** Search or filtering absent. Connected vs. available integrations not visually differentiated.

---

> **[Companion]** Phase 1 complete. ux_agent produced a 7-item pain point inventory. The Billing content-order issue (item 2) directly explains the 62 % bounce. No deep-link URLs (item 1) compounds every other issue. Routing to architect_agent + ui_agent for Phase 2.

---

### Phase 2 — Solution Design

**Agent:** `architect_agent` + `ui_agent`

#### architect_agent — Information Architecture Proposal

**Navigation model change:** Replace opaque index-state tab switching with React Router v6 nested routes.

```
/settings                     → redirect → /settings/profile
/settings/profile
/settings/security
/settings/notifications
/settings/billing
/settings/billing/invoices    → sub-route (offloads InvoiceTable)
/settings/team
/settings/team/:memberId      → sub-route (RoleEditor as drawer)
/settings/integrations
```

**State management change:** Lift shared settings state into a `SettingsContext` (React Context + useReducer). Eliminate prop-drilling. Each section subscribes only to its own slice.

**Dirty-state guard:** Implement `useUnsavedChanges` hook that intercepts React Router navigation events and triggers a confirmation dialog when form state is dirty.

#### ui_agent — Visual Hierarchy Fixes

**BillingSection reorder (highest priority):**
```
Before: PlanSummary → InvoiceTable → UsageMetrics → PaymentMethodForm
After:  PlanSummary → PaymentMethodForm → UsageMetrics → InvoiceTable (collapsed accordion)
```

**NotificationsSection grouping:**
```
Group A: "Product Updates"   — in-app banners, release notes
Group B: "Activity Alerts"   — mentions, task assignments, due dates
Group C: "Billing & Admin"   — payment receipts, seat limit warnings
Group D: "Marketing"         — newsletters, feature announcements (opt-out default)
```

**DangerZone isolation:** Extract `DangerZone` from `ProfileSection`. Render as a standalone page section at `/settings/profile#danger-zone` with a red border card, 48 px top margin, and a two-step confirmation (type org name to confirm).

**IntegrationsSection grid + filter bar:**
- Replace flat list with 3-column responsive grid.
- Add filter bar: All | Connected | Available | Category dropdown.
- Connected integrations show a green status badge + "Manage" CTA; available show "Connect".

---

> **[Companion]** Phase 2 complete. architect_agent and ui_agent have agreed on: (a) route-per-section, (b) Context + useReducer state lift, (c) BillingSection content reorder, (d) Notifications grouping into 4 buckets, (e) DangerZone extraction. Routing to execution_agent for Phase 3 full audit report.

---

### Phase 3 — Implementation

**Agent:** `execution_agent`

**Full Audit Report — Settings Page UX**
*App: [B2B SaaS] — Audit date: 2026-06-27*

---

#### Severity-Rated Findings

| ID | Severity | Component | Finding | User Impact | Effort |
|----|----------|-----------|---------|-------------|--------|
| F-01 | CRITICAL | `SettingsContent` | No URL routing per section. Browser back exits app. Deep-link sharing impossible. Breaks user orientation on every navigation. | All users; every visit | M |
| F-02 | CRITICAL | `BillingSection` | `PaymentMethodForm` rendered below `InvoiceTable` (DOM position 4 of 4). Primary CTA invisible without scroll. Directly causes 62 % Billing bounce. | Billing admins | S |
| F-03 | HIGH | `ProfileForm` | No dirty-state guard. Unsaved form changes silently dropped on tab switch. Users lose work with no warning. | Any user editing profile | S |
| F-04 | HIGH | `TwoFactorPanel` | Fetches TOTP seed on every mount regardless of 2FA status. 800–1200 ms spinner blocks interaction even for users with 2FA already enabled. | Security-sensitive users | S |
| F-05 | HIGH | `DangerZone` | Delete-account action co-located with profile editing UI. Insufficient visual separation. Single-modal confirmation insufficient for irreversible action. | All admins | S |
| F-06 | MEDIUM | `NotificationsSection` | 22 ungrouped toggles. No category headers. Users cannot predict consequences of toggles; "Alert Rules" label unexplained. | All users | M |
| F-07 | MEDIUM | `SettingsContent` | Prop-drilling `activeSection` through 3 layers causes full-page re-renders on tab switch. Perceptible jank on low-end hardware (Lighthouse TBT +340 ms). | Users on mid-range devices | L |
| F-08 | MEDIUM | `IntegrationsSection` | Flat list of 14 integration cards. No search, no filter, no connected/available differentiation. Users cannot locate target integration efficiently. | Power users | M |
| F-09 | LOW | `SessionList` | Session rows show raw ISO timestamps (`2026-06-21T08:14:33Z`). No relative time ("5 days ago") or location context. | Security-aware users | S |
| F-10 | LOW | `AvatarUpload` | Accepts any image type; silently fails on HEIC format (common on iOS). No file type hint in upload label. | Mobile-first users | S |

*Effort key: S = Small (< 1 day), M = Medium (1–3 days), L = Large (> 3 days)*

---

#### Component-Level Notes

**`BillingSection` (F-02 deep-dive)**
The component renders children in this order:
```tsx
// Current — PROBLEMATIC
<PlanSummary />
<InvoiceTable limit={5} />      // 280 px minimum height
<UsageMetrics chartType="bar" />
<PaymentMethodForm />           // primary CTA — never seen
```
Fix: reorder and collapse `InvoiceTable` into an accordion default-closed:
```tsx
// Proposed
<PlanSummary />
<PaymentMethodForm />
<UsageMetrics chartType="bar" />
<Accordion label="Invoice History" defaultOpen={false}>
  <InvoiceTable limit={10} />
</Accordion>
```

**`SettingsContent` (F-07 deep-dive)**
Current state threading:
```
SettingsPage → [activeSection, setActiveSection]
  └─ SettingsContent → [activeSection, setActiveSection]
       └─ SettingsSidebar → activeSection (read), setActiveSection (write)
       └─ [ActiveSectionComponent] → activeSection (read)
```
Replace with `SettingsContext`:
```tsx
const SettingsContext = createContext<SettingsContextValue>(null!);
export const useSettings = () => useContext(SettingsContext);
```
Each section reads only its own slice; sidebar reads only `activeSection`. Full-page re-render eliminated.

---

> **[Companion]** Phase 3 complete. execution_agent produced 10 findings: 2 CRITICAL, 3 HIGH, 3 MEDIUM, 2 LOW. F-01 and F-02 are the root causes of the reported confusion and Billing bounce. Routing to reviewer_agent for Phase 4 consistency check.

---

### Phase 4 — Review

**Agent:** `reviewer_agent`

**Consistency Review — Settings Audit Findings**

Checked against: pain point inventory (Phase 1), architecture proposal (Phase 2), audit table (Phase 3).

| Check | Result | Note |
|-------|--------|------|
| All Phase 1 pain points mapped to findings | PASS | 7 pain points → 10 findings (items 3 & 7 expanded into separate findings) |
| Severity assignments internally consistent | PASS | Both CRITICAL findings have direct, measurable user-impact evidence |
| F-02 severity justified | PASS | 62 % bounce is a hard metric; CRITICAL rating appropriate |
| F-07 severity (MEDIUM not HIGH) justified | PASS | Performance issue, not a blocker; Lighthouse TBT delta noted |
| Proposed architecture addresses all CRITICAL/HIGH findings | PASS | Route-per-section resolves F-01; BillingSection reorder resolves F-02; `useUnsavedChanges` resolves F-03; lazy TOTP seed fetch resolves F-04; `DangerZone` extraction resolves F-05 |
| Effort estimates consistent with change scope | PASS | No small-effort items misclassified as large |
| Any findings without proposed resolution | FLAG | F-09 (ISO timestamps) and F-10 (HEIC upload) are LOW severity but have no explicit fix in Phase 2 proposal |

**Reviewer recommendations:**
1. Add F-09 fix to handoff: replace raw ISO strings with `formatDistanceToNow` (date-fns) + `title` attribute for full timestamp on hover.
2. Add F-10 fix to handoff: set `accept="image/png,image/jpeg,image/webp"` on the file input; add helper text "PNG, JPG, or WebP, max 5 MB".
3. Confirm with product: does `DigestFrequency` belong in Group B or Group C of the Notifications redesign? Currently unassigned.

---

> **[Companion]** Phase 4 complete. reviewer_agent found no critical inconsistencies. Two LOW-severity findings (F-09, F-10) lacked explicit fixes — added to handoff list. One open question for product on `DigestFrequency` grouping. Routing to orchestrator for Phase 5 handoff.

---

### Phase 5 — Handoff

**Agent:** `orchestrator`

**Handoff Package — Settings Page Redesign**
*Recipient: Frontend Engineering + Product Design*

#### Prioritized Action List

**Sprint 1 — CRITICAL (unblock Billing conversion)**
- [ ] **F-02** Reorder `BillingSection` children: `PlanSummary` → `PaymentMethodForm` → `UsageMetrics` → `InvoiceTable` (accordion, default closed). Estimated: 0.5 days.
- [ ] **F-01** Implement React Router v6 nested routes for all six sections. Add redirect from `/settings` → `/settings/profile`. Estimated: 2 days.

**Sprint 2 — HIGH (prevent data loss + security)**
- [ ] **F-03** Implement `useUnsavedChanges` hook; wire to `ProfileForm`, `NotificationsSection`, `BillingSection` payment form. Estimated: 1 day.
- [ ] **F-04** Lazy-load TOTP seed in `TwoFactorPanel`: fetch only when user clicks "Enable 2FA", not on mount. Estimated: 0.5 days.
- [ ] **F-05** Extract `DangerZone` to isolated card section. Add two-step confirmation (type org name). Estimated: 1 day.

**Sprint 3 — MEDIUM (reduce cognitive load)**
- [ ] **F-06** Restructure `NotificationsSection` into 4 labeled groups (Product Updates / Activity Alerts / Billing & Admin / Marketing). Estimated: 1.5 days. *Note: confirm `DigestFrequency` placement with product before starting.*
- [ ] **F-07** Lift state to `SettingsContext` (useReducer). Eliminate prop-drilling in `SettingsContent`. Estimated: 3 days.
- [ ] **F-08** Add filter bar + connected/available badges to `IntegrationsSection`. Switch flat list to 3-column grid. Estimated: 2 days.

**Sprint 4 — LOW (polish)**
- [ ] **F-09** Replace ISO timestamps in `SessionList` with `formatDistanceToNow` (date-fns); add `title` attribute for exact time on hover. Estimated: 0.5 days.
- [ ] **F-10** Restrict `AvatarUpload` accept attribute to `image/png,image/jpeg,image/webp`; add helper text. Estimated: 0.5 days.

---

## 4. Final Output Artifact

### Severity-Rated Findings Table

| ID | Severity | Component | Root Cause | Business Impact |
|----|----------|-----------|------------|-----------------|
| F-01 | **CRITICAL** | `SettingsContent` | No per-section routing | Disorientation; no shareability |
| F-02 | **CRITICAL** | `BillingSection` | Wrong child render order | 62 % Billing bounce rate |
| F-03 | **HIGH** | `ProfileForm` | No dirty-state guard | Silent data loss on tab switch |
| F-04 | **HIGH** | `TwoFactorPanel` | Eager TOTP seed fetch | 800–1200 ms unnecessary spinner |
| F-05 | **HIGH** | `DangerZone` | Co-located with safe actions | Accidental irreversible deletion risk |
| F-06 | **MEDIUM** | `NotificationsSection` | 22 ungrouped toggles | User confusion; wrong opt-outs |
| F-07 | **MEDIUM** | `SettingsContent` | Prop-drilled activeSection | Jank on tab switch; TBT +340 ms |
| F-08 | **MEDIUM** | `IntegrationsSection` | Flat unfiltered list | Integration not found; drop-off |
| F-09 | **LOW** | `SessionList` | Raw ISO timestamps | Poor security UX legibility |
| F-10 | **LOW** | `AvatarUpload` | No file type restriction | Silent HEIC upload failure |

---

### Proposed Component Hierarchy

```
<SettingsProvider>                    // Context + useReducer; replaces prop-drilling
  <SettingsLayout>
    <SettingsSidebar />               // reads activeSection from context; nav links = <NavLink>
    <Routes>
      <Route path="profile">
        <ProfileHeader />
        <ProfileForm />               // useUnsavedChanges hook
        <DangerZoneCard />            // ← extracted; two-step confirm
      </Route>

      <Route path="security">
        <PasswordForm />
        <TwoFactorPanel lazy />       // TOTP seed fetched on user action only
        <SessionList humanTime />     // formatDistanceToNow
      </Route>

      <Route path="notifications">
        <NotificationGroup label="Product Updates">
          <ChannelToggles scope="product" />
        </NotificationGroup>
        <NotificationGroup label="Activity Alerts">
          <ChannelToggles scope="activity" />
          <DigestFrequency />
        </NotificationGroup>
        <NotificationGroup label="Billing & Admin">
          <ChannelToggles scope="billing" />
        </NotificationGroup>
        <NotificationGroup label="Marketing" optOutDefault>
          <ChannelToggles scope="marketing" />
        </NotificationGroup>
      </Route>

      <Route path="billing">
        <PlanSummary />
        <PaymentMethodForm />         // ← promoted to position 2
        <UsageMetrics />
        <Accordion label="Invoice History" defaultOpen={false}>
          <InvoiceTable />
        </Accordion>
      </Route>

      <Route path="billing/invoices"> // sub-route for full invoice view
        <InvoiceTable full />
      </Route>

      <Route path="team">
        <InviteForm />                // ← promoted above MemberTable
        <MemberTable />
      </Route>

      <Route path="team/:memberId">   // sub-route; renders as side drawer
        <RoleEditor />
      </Route>

      <Route path="integrations">
        <IntegrationFilterBar />      // All | Connected | Available | Category
        <IntegrationGrid>             // 3-column responsive
          <IntegrationCard />         // connected: green badge + Manage CTA
        </IntegrationGrid>
        <WebhookForm />
      </Route>
    </Routes>
  </SettingsLayout>
</SettingsProvider>
```

**Total findings: 10 | CRITICAL: 2 | HIGH: 3 | MEDIUM: 3 | LOW: 2**
**Estimated total engineering effort: ~13 days across 4 sprints**
**Expected primary outcome: Billing task-completion rate 38 % → ≥ 75 %**
