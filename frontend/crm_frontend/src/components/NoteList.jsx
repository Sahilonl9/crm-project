import { useState, useEffect } from "react";
import api from "../api/axiosInstance";
import "./NoteList.css";

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function NoteList({ leadId }) {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editContent, setEditContent] = useState("");

  const fetchNotes = async () => {
    try {
      const { data } = await api.get(`/leads/${leadId}/notes/`);
      setNotes(Array.isArray(data) ? data : data.results || []);
    } catch (_) {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, [leadId]);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    setSaving(true);
    try {
      const { data } = await api.post(`/leads/${leadId}/notes/`, { content });
      setNotes((prev) => [data, ...prev]);
      setContent("");
    } catch (_) {
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this note?")) return;

    try {
      await api.delete(`/leads/${leadId}/notes/${id}/`);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    } catch (_) {}
  };

  const startEdit = (note) => {
    setEditId(note.id);
    setEditContent(note.content);
  };

  const handleEdit = async (id) => {
    if (!editContent.trim()) return;

    try {
      const { data } = await api.patch(`/leads/${leadId}/notes/${id}/`, {
        content: editContent,
      });
      setNotes((prev) => prev.map((n) => (n.id === id ? data : n)));
      setEditId(null);
    } catch (_) {}
  };

  return (
    <div className="note-list">
      <div className="note-list-header">
        <h3 className="note-list-title">Notes</h3>
        <span className="note-list-count">{notes.length}</span>
      </div>

      <form className="note-add" onSubmit={handleAdd}>
        <textarea
          className="form-textarea"
          placeholder="Add a note..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={2}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleAdd(e);
          }}
        />
        <div className="note-add-footer">
          <span className="note-add-hint">Ctrl/Cmd + Enter to save</span>
          <button
            type="submit"
            className="btn btn-primary btn-sm"
            disabled={saving || !content.trim()}
          >
            {saving ? "Saving..." : "Add Note"}
          </button>
        </div>
      </form>

      {loading ? (
        <div className="note-list-loading"><div className="spinner" /></div>
      ) : notes.length === 0 ? (
        <div className="note-list-empty">No notes yet. Add the first one above.</div>
      ) : (
        <div className="note-items">
          {notes.map((note) => (
            <div key={note.id} className="note-item animate-fade">
              <div className="note-item-header">
                <span className="note-author">{note.author_name}</span>
                <span className="note-time">{timeAgo(note.created_at)}</span>
                <div className="note-item-actions">
                  <button className="btn btn-ghost btn-sm" onClick={() => startEdit(note)}>
                    Edit
                  </button>
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ color: "var(--red)" }}
                    onClick={() => handleDelete(note.id)}
                  >
                    Del
                  </button>
                </div>
              </div>

              {editId === note.id ? (
                <div className="note-edit">
                  <textarea
                    className="form-textarea"
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={2}
                  />
                  <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => setEditId(null)}>
                      Cancel
                    </button>
                    <button className="btn btn-primary btn-sm" onClick={() => handleEdit(note.id)}>
                      Save
                    </button>
                  </div>
                </div>
              ) : (
                <p className="note-content">{note.content}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
