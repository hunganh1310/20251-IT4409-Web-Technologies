
import React, { useState } from "react";
import "../styles/MainContent/SettingsExtra.css";

function SettingsExtra() {
  const [tab, setTab] = useState("General");
  const [form, setForm] = useState({
    name: "",
    email: "",
    theme: "light",
    language: "en",
    notifications: true,
    privacy: "standard",
    security: "medium",
    twoFactor: false,
    backupCodes: false,
    accentColor: "#007bff"
  });

  const renderFields = () => {
    switch (tab) {
      case "General":
        return <>
          <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Name" />
          <input value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="Email" />
          <select value={form.language} onChange={e => setForm({ ...form, language: e.target.value })}>
            <option value="en">English</option>
            <option value="vi">Vietnamese</option>
            <option value="jp">Japanese</option>
          </select>
        </>;
      case "Theme":
        return <>
          <select value={form.theme} onChange={e => setForm({ ...form, theme: e.target.value })}>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
          <input type="color" value={form.accentColor} onChange={e => setForm({ ...form, accentColor: e.target.value })} />
        </>;
      case "Security":
        return <>
          <select value={form.security} onChange={e => setForm({ ...form, security: e.target.value })}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <label>
            <input type="checkbox" checked={form.twoFactor} onChange={e => setForm({ ...form, twoFactor: e.target.checked })} />
            Enable 2FA
          </label>
          <label>
            <input type="checkbox" checked={form.backupCodes} onChange={e => setForm({ ...form, backupCodes: e.target.checked })} />
            Enable Backup Codes
          </label>
        </>;
      case "Advanced":
        return <>
          <select value={form.privacy} onChange={e => setForm({ ...form, privacy: e.target.value })}>
            <option value="standard">Standard</option>
            <option value="private">Private</option>
            <option value="public">Public</option>
          </select>
          <label>
            <input type="checkbox" checked={form.notifications} onChange={e => setForm({ ...form, notifications: e.target.checked })} />
            Enable Notifications
          </label>
        </>;
      default:
        return null;
    }
  };

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
            {renderFields()}
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
