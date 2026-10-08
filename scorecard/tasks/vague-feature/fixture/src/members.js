const members = [
  { id: 1, name: "Dana Reyes", email: "dana@example.test", plan: "team", joined: "2026-01-14" },
  { id: 2, name: "Omar Haddad", email: "omar@example.test", plan: "solo", joined: "2026-03-02" },
];

function listMembers() {
  return members.map((m) => ({ ...m }));
}

module.exports = { listMembers };
