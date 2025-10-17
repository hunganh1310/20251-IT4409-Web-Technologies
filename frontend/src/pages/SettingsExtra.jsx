import React, { useState } from "react";
import "../styles/MainContent/SettingsExtra.css";

function SettingsExtra() {
  const [tab, setTab] = useState("General");
  const [form, setForm] = useState({ name: "", email: "", theme: "light" });

  
  const renderMany = () => {
    const blocks = [];
    for (let i = 0; i < 12; i++) {
      blocks.push(
        <div className="settings-extra-section" key={i}>
          <div className="settings-extra-tabs">
            {["General", "Security", "Theme", "Advanced"].map(t => (
              <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>{t} {i + 1}</button>
            ))}
          </div>
          <form className="settings-extra-form">
            <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Name" />
            <input value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="Email" />
            <select value={form.theme} onChange={e => setForm({ ...form, theme: e.target.value })}>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
            <button type="button">Save</button>
          </form>
        </div>
      );
    }
    return blocks;
  };

  return <div className="settings-extra-root">{renderMany()}</div>;
}

export default SettingsExtra;
