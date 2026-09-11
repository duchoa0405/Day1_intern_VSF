# FashionRev-Ops: Revenue & Net Profit Management System

> **Financial & operational management platform tailored for fast-fashion online retail (Ready-to-wear / Pre-stocked apparel).**

---

## 1. Business Context & Core Problems

Fast-fashion e-commerce operates on rapid inventory turnover but faces severe margin leakage risks:

1. **Short Trend Lifecycle:** Apparel trends last only 2–4 weeks. Without real-time tracking of net margins and velocity by variant (Size/Color/Form), previous profits get trapped in slow-moving stock (*"Paper Profit, Negative Cash Flow"*).
2. **Volatile Landed Costs:** Wholesale prices, freight charges, and currency rates fluctuate per batch. COGS cannot be treated as a static number.
3. **High Return Rates (15%–30%):** Returns cause 2-way shipping costs, damaged packaging, rework labor, and complete COGS loss for unsellable items.
4. **Marketplace Fee Leakage:** Undetected overcharges (weight discrepancies, shifting platform fees, campaign deductions) erode 3%–7% of revenue.

---

## 2. Core System Pillars

```mermaid
flowchart TD
    A[Supplier / Factory] -->|1. PO + Freight Cost| B(Landed Cost Allocation Engine)
    B -->|2. Inbound & Barcode Labeling| C[Variant Inventory]
    C -->|3. Order Dispatch & COGS Snapshot| D[Channels: TikTok / Shopee / FB]
    D -->|4. Delivered Successfully| E[Wallet Reconciliation & P&L]
    D -->|4. Customer Returned| F[Return Loss Accounting]
    E --> G[Real Net Profit Dashboard]
    F --> G
```

### Landed Cost Allocation
Automatically allocates freight and packaging into each unit cost:
$$\text{Landed Cost}_{\text{SKU}} = \text{Wholesale Price} + \frac{\text{Total Inbound Freight} + \text{Handling Fees}}{\text{Total Units Received}} + \text{Packaging/Tag Cost}$$

### Accurate FIFO & COGS Snapshot
- Depletes inventory based on **First-In, First-Out (FIFO)** per batch.
- Freezes (`applied_landed_cogs`) onto each order item at fulfillment time to maintain historical reporting integrity.

### Return Loss Accounting
- **Intact returns:** Restocked. Loss recorded = 2-way shipping + damaged polybags + rework cost.
- **Damaged/Swapped items:** Moved to clearance. **100% COGS loss** is booked immediately.

### Marketplace Reconciliation
Matches bank payouts with order records to uncover weight penalties, campaign fee discrepancies, and payment gateway charges.

---

## 3. Core Scope (MVP - 11/09/2026)

### Feature 1: Inbound Landed Cost Engine (True Warehouse Inbound Cost)
* **Business Problem & Purpose:** Prevents distorted profit margins caused by static wholesale costing. In ready-to-wear fashion, when ordering 500 units at 75,000 VND ($3.00) with a 1,000,000 VND ($40.00) bulk truck freight fee and 1,000 VND polybag tag surcharge, the true landed unit cost is **78,000 VND ($3.12)**, not 75,000 VND.
* **Core Capabilities & Interactive UI/UX:**
  - **Live Landed Cost Calculator:** Real-time dynamic cost distribution preview as freight and handling fees are entered before finalizing the PO.
  - **Transparent Cost Formula per SKU:**
    $$\text{Landed Cost}_{\text{SKU}} = \text{Wholesale Unit Price} + \frac{\text{Total Bulk Freight} + \text{Handling}}{\text{Total Units Received}} + \text{Polybag/Tag Cost}$$
  - **Automated Inventory Inbound:** Instantly syncs PO records, increments variant stock by size/color, and generates SKU barcodes for polybag labeling.

### Feature 2: Product & Order Net Profit Engine (True Take-Home Margin)
* **Business Problem & Purpose:** Solves the *"High Revenue, Empty Wallet"* trap. Selling a 189,000 VND dress on TikTok Shop / Shopee gets eroded by platform commission, payment processing, campaign vouchers, packaging polybags, and return shrinkage. Directly answers: *"How much real cash does each product and order actually bring to the shop?"*
* **Core Capabilities & Interactive UI/UX:**
  - **Financial Waterfall Breakdown:** Visual step-by-step cashflow deduction for every order item:
    $$\text{Gross Customer Payment} \rightarrow -\text{Landed COGS} \rightarrow -\text{Platform Fees} \rightarrow -\text{Packaging} \rightarrow -\text{Return Losses} = \mathbf{\text{True Net Profit}}$$
  - **Real-Time Profitability Indicators:** Dynamic color-coded badges showing exact net cash profit and net margin percentage (`Net Margin %`).
  - **Interactive Return Loss Accounting:** One-click financial triage to immediately reflect return losses:
    - *Intact Return:* Restocked; loss booked = 2-way shipping + damaged packaging (e.g., -35,000 VND).
    - *Damaged / Swapped Return:* Sent to clearance; **100% unit COGS is written off** as shrinkage loss.

---

## 4. Database Schema

```mermaid
erDiagram
    PRODUCTS_VARIANTS ||--o{ PURCHASE_ORDER_ITEMS : contains
    PURCHASE_ORDERS ||--|{ PURCHASE_ORDER_ITEMS : includes
    PRODUCTS_VARIANTS ||--o{ ORDER_ITEMS : ordered_in
    ORDERS ||--|{ ORDER_ITEMS : contains

    PRODUCTS_VARIANTS {
        bigint id PK
        string sku UK "e.g., TEE-BLK-L"
        string product_name
        string color
        string size
        string barcode
        int stock_quantity
        decimal base_price
    }

    PURCHASE_ORDERS {
        bigint id PK
        string po_code UK "e.g., PO-20260911-001"
        string supplier_name
        decimal total_merchandise_cost
        decimal shipping_fee
        decimal other_fees
        int total_quantity
        string status "DRAFT | CONFIRMED | RECEIVED"
        datetime created_at
    }

    PURCHASE_ORDER_ITEMS {
        bigint id PK
        bigint po_id FK
        bigint variant_id FK
        int quantity
        decimal unit_cost
        decimal allocated_freight
        decimal landed_cost
    }

    ORDERS {
        bigint id PK
        string order_sn UK "Marketplace Order ID"
        string platform "TIKTOK | SHOPEE | FACEBOOK | OFFLINE"
        decimal gross_sales
        decimal platform_fee
        decimal shipping_fee_shop
        string order_status "PENDING | DELIVERED | RETURNED | CANCELLED"
        string return_condition "NONE | INTACT | DAMAGED"
        decimal return_loss_cost
        decimal net_settlement_amount
        datetime order_date
    }

    ORDER_ITEMS {
        bigint id PK
        bigint order_id FK
        bigint variant_id FK
        int quantity
        decimal selling_price
        decimal applied_landed_cogs "Frozen COGS snapshot"
        decimal net_profit
    }
```

---

## 5. Role-Based Access Control (RBAC)

| Role | Key Responsibility | System Permissions |
| :--- | :--- | :--- |
| **Owner / Admin** | Overall profitability, strategic pricing, inventory budget | Full access; view real-time P&L, return rate & turnover metrics |
| **Accountant** | Cashflow reconciliation, fee audit, expense tracking | Reconcile marketplace payouts, record OPEX & ledger entries |
| **Operations / Warehouse** | Inbound receiving, barcode labeling, return grading | Manage POs, print SKU barcodes, process return inspections |
| **Marketing Lead** | Ads performance, product trend analysis | Access item-level net margin to optimize ROAS & ad budget |

---

## 6. Implementation Roadmap

- [x] **Phase 1 (11/09/2026 - Core Inbound & Landed Cost Engine):**
  - Variant catalog management (SKU, Color, Size, Barcode).
  - PO creation with automated Landed Cost allocation.
  - Order fulfillment with FIFO COGS snapshot & margin calculation.
- [ ] **Phase 2 (Return Operations & Reconciliation):**
  - Barcode scanner integration for return triage (Intact vs Damaged).
  - Automated statement import for Shopee / TikTok Shop fee reconciliation.
- [ ] **Phase 3 (Inventory Velocity & Deadstock Intelligence):**
  - SKU-level sales velocity tracking.
  - 20-day slow-moving/deadstock alerts to trigger markdown workflows.

---

## 7. Getting Started

### Prerequisites
- Python 3.10+ / Node.js 18+
- Relational Database: PostgreSQL / MySQL / SQLite

### Standard Workflow
1. **Step 1:** Create product catalog and define variant SKUs.
2. **Step 2:** Generate Purchase Order (PO) with wholesale costs and freight fee $\rightarrow$ System auto-calculates **Landed Cost**.
3. **Step 3:** Print SKU barcode labels and attach them to polybags upon receiving.
4. **Step 4:** Fulfill incoming sales orders $\rightarrow$ System freezes COGS via FIFO and calculates net profit per item in real time.
