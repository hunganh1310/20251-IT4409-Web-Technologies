import React, { useState } from "react";
import "../styles/MainContent/AdminCrudExtra.css";

function AdminCrudExtra() {
  const [items, setItems] = useState([]);
  const [input, setInput] = useState("");

  const handleAdd = () => {
    if (input.trim()) setItems([...items, input]);
    setInput("");
  };

  const handleRemove = (idx) => {
    setItems(items.filter((_, i) => i !== idx));
  };

  
  const renderMany = () => {
    const blocks = [];
    for (let i = 0; i < 15; i++) {
      blocks.push(
        <div className="admincrud-extra-section" key={i}>
          <h2>Admin CRUD Section {i + 1}</h2>
          <form onSubmit={e => { e.preventDefault(); handleAdd(); }}>
            <input value={input} onChange={e => setInput(e.target.value)} placeholder="Add item" />
            <button type="submit">Add</button>
          </form>
          <table className="admincrud-extra-table">
            <thead><tr><th>#</th><th>Item</th><th>Action</th></tr></thead>
            <tbody>
              {items.map((item, idx) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td>{item}</td>
                  <td><button onClick={() => handleRemove(idx)}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    return blocks;
  };

  return <div className="admincrud-extra-root">{renderMany()}</div>;
}

export default AdminCrudExtra;
