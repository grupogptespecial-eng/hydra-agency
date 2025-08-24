import React from 'react';

export const LeftPanel: React.FC = () => (
  <div>
    <label>
      Start
      <input type="date" />
    </label>
    <label>
      End
      <input type="date" />
    </label>
    <label>
      Slicing
      <select>
        <option value="fixed-window">Fixed</option>
        <option value="rolling">Rolling</option>
        <option value="custom">Custom</option>
      </select>
    </label>
  </div>
);
