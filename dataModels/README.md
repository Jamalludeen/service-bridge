**Service & Booking Data Models**

- Visual diagram: [service_booking.svg](service_booking.svg)
- Source PlantUML: [service_booking.puml](service_booking.puml)

Notes:

- Use `id` fields as primary keys for references.
- `quantity` applies when `Service.pricing_type == PER_UNIT`.
- `estimated_price` is server-calculated; client should treat `final_price` as authoritative when present.

If you need PNG or separate SVGs for each model, tell me and I'll add them.

<!-- Embedded graphical UML for easy sharing with frontend/mobile teams -->

<details>
<summary>Embedded diagram (expand to view)</summary>

<!-- inline SVG diagram (self-contained) -->
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="520" viewBox="0 0 1000 520">
	<style>
		.cls-rect { fill: #f8f9fb; stroke: #2b2d42; stroke-width: 1.5 }
		.cls-title { font: bold 14px sans-serif; fill: #2b2d42 }
		.cls-field { font: 12px monospace; fill: #222 }
		.cls-note { font: 12px sans-serif; fill: #555 }
		.arrow { stroke: #2b2d42; stroke-width: 1.4; fill: none; marker-end: url(#arrowhead) }
	</style>
	<defs>
		<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
			<polygon points="0 0, 10 3.5, 0 7" fill="#2b2d42" />
		</marker>
	</defs>

    <!-- Service box -->
    <rect class="cls-rect" x="40" y="40" width="340" height="180" rx="6"/>
    <text class="cls-title" x="60" y="66">Service</text>
    <text class="cls-field" x="60" y="92">id: Integer (PK)</text>
    <text class="cls-field" x="60" y="112">professional_id: FK &gt; Professional</text>
    <text class="cls-field" x="60" y="132">category_id: FK &gt; ServiceCategory</text>
    <text class="cls-field" x="60" y="152">title: CharField</text>
    <text class="cls-field" x="60" y="172">pricing_type: Enum(HOURLY,DAILY,FIXED,PER_UNIT)</text>
    <text class="cls-field" x="60" y="192">price_per_unit: Decimal</text>

    <!-- Booking box -->
    <rect class="cls-rect" x="420" y="40" width="520" height="300" rx="6"/>
    <text class="cls-title" x="440" y="66">Booking</text>
    <text class="cls-field" x="440" y="92">id: Integer (PK)</text>
    <text class="cls-field" x="440" y="112">customer_id: FK &gt; CustomerProfile</text>
    <text class="cls-field" x="440" y="132">professional_id: FK &gt; Professional</text>
    <text class="cls-field" x="440" y="152">service_id: FK &gt; Service</text>
    <text class="cls-field" x="440" y="172">scheduled_date: Date</text>
    <text class="cls-field" x="440" y="192">scheduled_time: Time</text>
    <text class="cls-field" x="440" y="212">address: Text</text>
    <text class="cls-field" x="440" y="232">quantity: Integer</text>
    <text class="cls-field" x="440" y="252">estimated_price: Decimal</text>
    <text class="cls-field" x="440" y="272">final_price: Decimal (nullable)</text>
    <text class="cls-field" x="440" y="292">status: Enum(PENDING,ACCEPTED,REJECTED,IN_PROGRESS,COMPLETED,CANCELLED)</text>

    <!-- BookingStatusHistory box -->
    <rect class="cls-rect" x="420" y="360" width="340" height="120" rx="6"/>
    <text class="cls-title" x="440" y="384">BookingStatusHistory</text>
    <text class="cls-field" x="440" y="404">id: Integer (PK)</text>
    <text class="cls-field" x="440" y="424">booking_id: FK &gt; Booking</text>
    <text class="cls-field" x="440" y="444">from_status: CharField</text>
    <text class="cls-field" x="440" y="464">to_status: CharField</text>

    <!-- Small referenced boxes -->
    <rect x="40" y="240" width="200" height="60" class="cls-rect" rx="6"/>
    <text class="cls-title" x="60" y="266">Professional</text>
    <text class="cls-field" x="60" y="288">id: Integer (FK target)</text>

    <rect x="40" y="320" width="200" height="60" class="cls-rect" rx="6"/>
    <text class="cls-title" x="60" y="346">CustomerProfile</text>
    <text class="cls-field" x="60" y="368">id: Integer (FK target)</text>

    <rect x="760" y="360" width="160" height="60" class="cls-rect" rx="6"/>
    <text class="cls-title" x="780" y="386">User</text>
    <text class="cls-field" x="780" y="408">id: Integer</text>

    <!-- Arrows / Relationships -->
    <path class="arrow" d="M 380 130 L 420 130" />
    <text class="cls-note" x="330" y="120">Service 1..* &lt;- Booking</text>

    <path class="arrow" d="M 240 270 L 420 110" />
    <text class="cls-note" x="180" y="260">Professional 1..* &lt;- Service</text>

    <path class="arrow" d="M 140 350 L 440 120" />
    <text class="cls-note" x="120" y="332">CustomerProfile 1..* &lt;- Booking</text>

    <path class="arrow" d="M 680 220 L 680 360" />
    <text class="cls-note" x="690" y="270">Booking 1..* &lt;- BookingStatusHistory</text>

    <path class="arrow" d="M 860 420 L 760 420" />
    <text class="cls-note" x="760" y="442">Booking.cancelled_by -> User (nullable)</text>

    <rect x="20" y="480" width="960" height="28" fill="#ffffff" />
    <text class="cls-note" x="30" y="498">Generated diagram: simplified visual for Flutter; use ids for relations and nested `service` summary (id, title, price_per_unit, pricing_type).</text>

</svg>

</details>

---

### PlantUML source

```plantuml
@startuml
title Service & Booking Model Diagram

' Entity classes from Django models
class Service {
	+id: Integer
	+professional_id: FK Professional
	+category_id: FK ServiceCategory
	+title: CharField
	+description: TextField
	+pricing_type: Enum(HOURLY,DAILY,FIXED,PER_UNIT)
	+price_per_unit: Decimal
	+is_active: Boolean
	+created_at: DateTime
}

class Booking {
	+id: Integer
	+customer_id: FK CustomerProfile
	+professional_id: FK Professional
	+service_id: FK Service
	+scheduled_date: Date
	+scheduled_time: Time
	+address: TextField
	+city: CharField
	+latitude: Decimal
	+longitude: Decimal
	+special_instructions: TextField
	+quantity: Integer
	+estimated_price: Decimal
	+final_price: Decimal
	+status: Enum(PENDING,ACCEPTED,REJECTED,IN_PROGRESS,COMPLETED,CANCELLED)
	+rejection_reason: TextField
	+cancellation_reason: TextField
	+cancelled_by_id: FK User (nullable)
	+created_at: DateTime
	+updated_at: DateTime
	+accepted_at: DateTime (nullable)
	+started_at: DateTime (nullable)
	+completed_at: DateTime (nullable)
}

class BookingStatusHistory {
	+id: Integer
	+booking_id: FK Booking
	+from_status: CharField
	+to_status: CharField
	+changed_by_id: FK User (nullable)
	+note: TextField
	+created_at: DateTime
}

' Small stubs for referenced models
class Professional
class ServiceCategory
class CustomerProfile
class User

' Relationships
Professional "1" -- "0..*" Service : offers >
Service "1" -- "0..*" Booking : has >
CustomerProfile "1" -- "0..*" Booking : places >
Professional "1" -- "0..*" Booking : receives >
Booking "1" -- "0..*" BookingStatusHistory : history >
Booking o-- User : cancelled_by

note bottom
Use primary keys `id` for references.
Clients should display nested `service` summary (id,title,price_per_unit,pricing_type).
@enduml
```

---

Notes:

- Use `id` fields as primary keys for references.
- `quantity` applies when `Service.pricing_type == PER_UNIT`.
- `estimated_price` is server-calculated; client should treat `final_price` as authoritative when present.

If you need PNG exports, separate per-model diagrams, or a ZIP of `dataModels`, tell me and I'll add them.
