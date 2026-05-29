import { useState, useEffect } from "react";
import PanelSection from "./PanelSection";

function toList(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function toNumber(value) {
  return value === "" ? undefined : Number(value);
}

export default function ResortUpdateForm({
  onSubmit,
  ownerId = "",
  ownedResorts = [],
}) {
  const [mode, setMode] = useState("update");
  const [form, setForm] = useState({
    resort_id: "",
    name: "",
    category: "",
    city: "Dandeli",
    location: "",
    latitude: "",
    longitude: "",
    phone: "",
    email: "",
    website: "",
    rating: "",
    review_count: "",
    rooms: "",
    description: "",
    unique_features: "",
    amenities: "",
    activities_onsite: "",
    activities_nearby: "",
    water_activities: "",
    food_options: "",
    family_friendly: false,
    romantic_couples: false,
    check_in: "",
    check_out: "",
    available_rooms: "",
    occupied_rooms: "",
    availability_status: "",
    special_offer: "",
    price: "",
  });

  const resetFormFields = () => {
    setForm({
      resort_id: "",
      name: "",
      category: "",
      city: "Dandeli",
      location: "",
      latitude: "",
      longitude: "",
      phone: "",
      email: "",
      website: "",
      rating: "",
      review_count: "",
      rooms: "",
      description: "",
      unique_features: "",
      amenities: "",
      activities_onsite: "",
      activities_nearby: "",
      water_activities: "",
      food_options: "",
      family_friendly: false,
      romantic_couples: false,
      check_in: "",
      check_out: "",
      available_rooms: "",
      occupied_rooms: "",
      availability_status: "",
      special_offer: "",
      price: "",
    });
  };

  useEffect(() => {
    function handleKeyDown(e) {
      const activeEl = document.activeElement;
      
      // Escape clears draft if focused on form elements, or just clears fields
      if (e.key === "Escape") {
        if (
          activeEl &&
          (activeEl.tagName === "INPUT" ||
            activeEl.tagName === "TEXTAREA" ||
            activeEl.tagName === "SELECT")
        ) {
          activeEl.blur();
        }
        e.preventDefault();
        resetFormFields();
        return;
      }

      // If typing in input, don't trigger mode shortcuts
      if (
        activeEl &&
        (activeEl.tagName === "INPUT" ||
          activeEl.tagName === "TEXTAREA" ||
          activeEl.tagName === "SELECT" ||
          activeEl.isContentEditable)
      ) {
        return;
      }

      if (e.key.toLowerCase() === "n") {
        e.preventDefault();
        setMode((current) => (current === "update" ? "create" : "update"));
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  function updateField(event) {
    const { name, type, checked, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function buildChanges() {
    const changes = {};

    const textFields = [
      "name",
      "category",
      "city",
      "location",
      "phone",
      "email",
      "website",
      "check_in",
      "check_out",
      "description",
      "unique_features",
      "availability_status",
      "special_offer",
    ];
    const numberFields = [
      "latitude",
      "longitude",
      "rating",
      "review_count",
      "price",
      "available_rooms",
      "occupied_rooms",
    ];
    const listFields = [
      "rooms",
      "amenities",
      "activities_onsite",
      "activities_nearby",
      "water_activities",
      "food_options",
    ];

    for (const field of textFields) {
      if (form[field].trim()) {
        changes[field] = form[field].trim();
      }
    }
    for (const field of numberFields) {
      const value = toNumber(form[field]);
      if (value !== undefined && !Number.isNaN(value)) {
        changes[field] = value;
      }
    }
    for (const field of listFields) {
      const value = toList(form[field]);
      if (value.length) {
        changes[field] = value;
      }
    }

    changes.family_friendly = form.family_friendly;
    changes.romantic_couples = form.romantic_couples;

    return changes;
  }

  function handleSubmit(e) {
    e.preventDefault();
    const changes = buildChanges();
    if (
      !ownerId.trim() ||
      (mode === "update" && !form.resort_id.trim()) ||
      !Object.keys(changes).length
    ) {
      return;
    }

    onSubmit?.({
      request_type: mode,
      resort_id: mode === "update" ? form.resort_id.trim() : null,
      owner_id: ownerId.trim(),
      submitted_by: ownerId.trim(),
      changes,
    });

    setForm((current) => ({
      ...current,
      resort_id: mode === "create" ? "" : current.resort_id,
      name: "",
      category: "",
      city: "Dandeli",
      location: "",
      latitude: "",
      longitude: "",
      phone: "",
      email: "",
      website: "",
      rating: "",
      review_count: "",
      rooms: "",
      description: "",
      unique_features: "",
      amenities: "",
      activities_onsite: "",
      activities_nearby: "",
      water_activities: "",
      food_options: "",
      family_friendly: false,
      romantic_couples: false,
      check_in: "",
      check_out: "",
      available_rooms: "",
      occupied_rooms: "",
      availability_status: "",
      special_offer: "",
      price: "",
    }));
  }

  return (
    <PanelSection
      kicker="Listing Management"
      title={mode === "create" ? "Create new listing" : "Update listing"}
      className="ops-form-panel"
    >
      <form onSubmit={handleSubmit}>
        <div
          className="ops-mode-toggle"
          role="tablist"
          aria-label="Submission type"
        >
          <button
            className={mode === "update" ? "active" : ""}
            type="button"
            onClick={() => setMode("update")}
          >
            Update Existing
          </button>
          <button
            className={mode === "create" ? "active" : ""}
            type="button"
            onClick={() => setMode("create")}
          >
            Add New Listing <kbd>N</kbd>
          </button>
        </div>

        {!ownerId.trim() ? (
          <div className="ops-empty small">
            Enter an owner ID above to enable submission.
          </div>
        ) : null}

        {/* Basic Information Section */}
        <fieldset style={{ border: "none", padding: 0, margin: "0 0 24px 0" }}>
          <legend style={{
            fontSize: "0.75rem",
            fontWeight: "600",
            color: "var(--ops-accent)",
            borderBottom: "1px solid var(--ops-border-light)",
            width: "100%",
            paddingBottom: "6px",
            marginBottom: "14px",
            textTransform: "uppercase",
            letterSpacing: "0.05em"
          }}>
            Basic details
          </legend>
          <div className="ops-form-grid">
            {mode === "update" ? (
              <label className="ops-field">
                <span>Select Resort</span>
                <select
                  name="resort_id"
                  value={form.resort_id}
                  onChange={updateField}
                  required
                >
                  <option value="">Choose your resort</option>
                  {ownedResorts.map((resort) => (
                    <option value={resort.id} key={resort.id}>
                      #{resort.id} {resort.name}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <>
                <label className="ops-field">
                  <span>Resort Name *</span>
                  <input
                    name="name"
                    value={form.name}
                    onChange={updateField}
                    placeholder="Kali River Hideaway"
                    required
                  />
                </label>
                <label className="ops-field">
                  <span>Category *</span>
                  <input
                    name="category"
                    value={form.category}
                    onChange={updateField}
                    placeholder="Eco Resort"
                    required
                  />
                </label>
                <label className="ops-field">
                  <span>City</span>
                  <input
                    name="city"
                    value={form.city}
                    onChange={updateField}
                    required
                  />
                </label>
                <label className="ops-field">
                  <span>Location *</span>
                  <input
                    name="location"
                    value={form.location}
                    onChange={updateField}
                    placeholder="Ganeshgudi Road"
                    required
                  />
                </label>
              </>
            )}

            <label className="ops-field">
              <span>Latitude</span>
              <input
                name="latitude"
                type="number"
                step="any"
                value={form.latitude}
                onChange={updateField}
                placeholder="15.2567"
              />
            </label>

            <label className="ops-field">
              <span>Longitude</span>
              <input
                name="longitude"
                type="number"
                step="any"
                value={form.longitude}
                onChange={updateField}
                placeholder="74.6421"
              />
            </label>

            <label className="ops-field">
              <span>Phone</span>
              <input
                name="phone"
                value={form.phone}
                onChange={updateField}
                placeholder="+91 9874516320"
              />
            </label>

            <label className="ops-field">
              <span>Email</span>
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={updateField}
                placeholder="info@resort.com"
              />
            </label>

            <label className="ops-field">
              <span>Website</span>
              <input
                name="website"
                value={form.website}
                onChange={updateField}
                placeholder="https://example.com"
              />
            </label>

            <label className="ops-field">
              <span>Check In Time</span>
              <input
                name="check_in"
                value={form.check_in}
                onChange={updateField}
                placeholder="12:30 PM"
              />
            </label>

            <label className="ops-field">
              <span>Check Out Time</span>
              <input
                name="check_out"
                value={form.check_out}
                onChange={updateField}
                placeholder="10:30 AM"
              />
            </label>
          </div>
        </fieldset>

        {/* Rating & Availability Section */}
        <fieldset style={{ border: "none", padding: 0, margin: "0 0 24px 0" }}>
          <legend style={{
            fontSize: "0.75rem",
            fontWeight: "600",
            color: "var(--ops-accent)",
            borderBottom: "1px solid var(--ops-border-light)",
            width: "100%",
            paddingBottom: "6px",
            marginBottom: "14px",
            textTransform: "uppercase",
            letterSpacing: "0.05em"
          }}>
            Rating & Booking Values
          </legend>
          <div className="ops-form-grid">
            <label className="ops-field">
              <span>Rating (0-5)</span>
              <input
                name="rating"
                type="number"
                min="0"
                max="5"
                step="0.1"
                value={form.rating}
                onChange={updateField}
              />
            </label>

            <label className="ops-field">
              <span>Review Count</span>
              <input
                name="review_count"
                type="number"
                min="0"
                value={form.review_count}
                onChange={updateField}
              />
            </label>

            <label className="ops-field">
              <span>Available Rooms</span>
              <input
                name="available_rooms"
                type="number"
                min="0"
                value={form.available_rooms}
                onChange={updateField}
              />
            </label>

            <label className="ops-field">
              <span>Occupied Rooms</span>
              <input
                name="occupied_rooms"
                type="number"
                min="0"
                value={form.occupied_rooms}
                onChange={updateField}
              />
            </label>

            <label className="ops-field">
              <span>Price Per Person</span>
              <input
                name="price"
                type="number"
                min="0"
                value={form.price}
                onChange={updateField}
              />
            </label>

            <label className="ops-field">
              <span>Availability Status</span>
              <select
                name="availability_status"
                value={form.availability_status}
                onChange={updateField}
              >
                <option value="">No change</option>
                <option value="open">Open</option>
                <option value="limited">Limited</option>
                <option value="sold out">Sold out</option>
                <option value="closed">Closed</option>
              </select>
            </label>
          </div>
        </fieldset>

        {/* Amenities & Activities Section */}
        <fieldset style={{ border: "none", padding: 0, margin: "0 0 24px 0" }}>
          <legend style={{
            fontSize: "0.75rem",
            fontWeight: "600",
            color: "var(--ops-accent)",
            borderBottom: "1px solid var(--ops-border-light)",
            width: "100%",
            paddingBottom: "6px",
            marginBottom: "14px",
            textTransform: "uppercase",
            letterSpacing: "0.05em"
          }}>
            Services & Experiences
          </legend>
          <div className="ops-form-grid">
            <label className="ops-field">
              <span>Room Types</span>
              <input
                name="rooms"
                value={form.rooms}
                onChange={updateField}
                placeholder="Treehouse, Standard Room, Suite"
              />
            </label>

            <label className="ops-field">
              <span>Amenities</span>
              <input
                name="amenities"
                value={form.amenities}
                onChange={updateField}
                placeholder="Garden, Restaurant, Parking, WiFi"
              />
            </label>

            <label className="ops-field">
              <span>Onsite Activities</span>
              <input
                name="activities_onsite"
                value={form.activities_onsite}
                onChange={updateField}
                placeholder="Bird watching, Nature walk"
              />
            </label>

            <label className="ops-field">
              <span>Nearby Activities</span>
              <input
                name="activities_nearby"
                value={form.activities_nearby}
                onChange={updateField}
                placeholder="Trekking, Jungle safari"
              />
            </label>

            <label className="ops-field">
              <span>Water Activities</span>
              <input
                name="water_activities"
                value={form.water_activities}
                onChange={updateField}
                placeholder="Kayaking, Rafting"
              />
            </label>

            <label className="ops-field">
              <span>Food Options</span>
              <input
                name="food_options"
                value={form.food_options}
                onChange={updateField}
                placeholder="Vegetarian, Non-Veg, Vegan"
              />
            </label>
          </div>
        </fieldset>

        {/* Flags Section */}
        <fieldset style={{ border: "none", padding: 0, margin: "0 0 24px 0" }}>
          <legend style={{
            fontSize: "0.75rem",
            fontWeight: "600",
            color: "var(--ops-accent)",
            borderBottom: "1px solid var(--ops-border-light)",
            width: "100%",
            paddingBottom: "6px",
            marginBottom: "14px",
            textTransform: "uppercase",
            letterSpacing: "0.05em"
          }}>
            Guest suitability
          </legend>
          <div className="ops-checkbox-row">
            <label>
              <input
                name="family_friendly"
                type="checkbox"
                checked={form.family_friendly}
                onChange={updateField}
              />
              Family Friendly
            </label>
            <label>
              <input
                name="romantic_couples"
                type="checkbox"
                checked={form.romantic_couples}
                onChange={updateField}
              />
              Romantic Getaway
            </label>
          </div>
        </fieldset>

        {/* Description Section */}
        <fieldset style={{ border: "none", padding: 0, margin: "0 0 24px 0", display: "flex", flexDirection: "column", gap: "12px" }}>
          <legend style={{
            fontSize: "0.75rem",
            fontWeight: "600",
            color: "var(--ops-accent)",
            borderBottom: "1px solid var(--ops-border-light)",
            width: "100%",
            paddingBottom: "6px",
            marginBottom: "14px",
            textTransform: "uppercase",
            letterSpacing: "0.05em"
          }}>
            Details & highlights
          </legend>
          <label className="ops-field">
            <span>Description</span>
            <textarea
              name="description"
              value={form.description}
              onChange={updateField}
              placeholder="Describe your resort experience..."
            />
          </label>

          <label className="ops-field">
            <span>Unique Features</span>
            <textarea
              name="unique_features"
              value={form.unique_features}
              onChange={updateField}
              placeholder="What makes your resort special?"
            />
          </label>

          <label className="ops-field">
            <span>Special Offers</span>
            <textarea
              name="special_offer"
              value={form.special_offer}
              onChange={updateField}
              placeholder="Describe any current promotions or special offers"
            />
          </label>
        </fieldset>

        <div className="ops-actions">
          <span style={{ fontSize: "0.7rem", color: "var(--ops-text-tertiary)", marginRight: "auto" }}>
            Press <kbd>Esc</kbd> to clear draft
          </span>
          <button
            className="ops-button primary"
            type="submit"
            disabled={!ownerId.trim()}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            Submit for Review
          </button>
        </div>
      </form>
    </PanelSection>
  );
}
