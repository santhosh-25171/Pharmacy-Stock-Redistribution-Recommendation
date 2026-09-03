import React, { useState } from 'react';
import { Building2, ArrowRight, ShieldCheck, MapPin, Truck } from 'lucide-react';

export const NetworkMap = ({ pharmacies = [], recommendations = [], onSelectPharmacy }) => {
  const [hoveredNode, setHoveredNode] = useState(null);

  // Normalize lat/lon into 0-100% SVG coordinates
  // Bangalore lat: 12.80 to 13.12, lon: 77.50 to 77.76
  const minLat = 12.80;
  const maxLat = 13.12;
  const minLon = 77.50;
  const maxLon = 77.76;

  const getCoordinates = (lat, lon) => {
    const x = ((lon - minLon) / (maxLon - minLon)) * 80 + 10;
    const y = (1 - (lat - minLat) / (maxLat - minLat)) * 80 + 10;
    return { x: Math.max(5, Math.min(95, x)), y: Math.max(5, Math.min(95, y)) };
  };

  const pharmacyCoords = {};
  pharmacies.forEach((p) => {
    pharmacyCoords[p.pharmacy_id] = {
      ...getCoordinates(p.latitude, p.longitude),
      data: p,
    };
  });

  // Top pending recommendations to render as transfer vectors
  const activeVectors = recommendations.slice(0, 15);

  return (
    <div className="relative w-full h-[450px] bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden p-4 select-none">
      {/* Background Grid & Radar rings */}
      <div className="absolute inset-0 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:24px_24px] opacity-30 pointer-events-none"></div>

      {/* Map Legend */}
      <div className="absolute top-4 left-4 z-10 p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs backdrop-blur-sm space-y-1.5 shadow-lg">
        <div className="font-bold text-white flex items-center gap-1.5">
          <MapPin className="w-3.5 h-3.5 text-emerald-400" />
          <span>Bengaluru Pharmacy Mesh</span>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-slate-300">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> Active</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500"></span> Maint</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-rose-500"></span> Closed</span>
          <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-emerald-400"></span> Transfer Vector</span>
        </div>
      </div>

      {/* SVG Network Graph */}
      <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Draw Transfer Lines */}
        {activeVectors.map((rec, idx) => {
          const src = pharmacyCoords[rec.source_pharmacy_id];
          const dest = pharmacyCoords[rec.destination_pharmacy_id];
          if (!src || !dest) return null;

          const isHovered = hoveredNode === rec.source_pharmacy_id || hoveredNode === rec.destination_pharmacy_id;

          return (
            <g key={idx}>
              <line
                x1={src.x}
                y1={src.y}
                x2={dest.x}
                y2={dest.y}
                stroke={isHovered ? '#10b981' : '#059669'}
                strokeWidth={isHovered ? '0.8' : '0.4'}
                strokeDasharray="1.5, 1"
                strokeOpacity={isHovered ? 0.9 : 0.45}
                className="transition-all duration-300"
              />
            </g>
          );
        })}

        {/* Draw Pharmacy Nodes */}
        {Object.entries(pharmacyCoords).map(([pId, node]) => {
          const isSelected = hoveredNode === pId;
          const status = node.data.operating_status;
          const nodeColor =
            status === 'CLOSED' ? '#f43f5e' : (status === 'MAINTENANCE' ? '#f59e0b' : '#10b981');
          
          return (
            <g
              key={pId}
              className="cursor-pointer group"
              onMouseEnter={() => setHoveredNode(pId)}
              onMouseLeave={() => setHoveredNode(null)}
              onClick={() => onSelectPharmacy && onSelectPharmacy(node.data)}
            >
              {/* Outer Pulse ring if active */}
              {status === 'ACTIVE' && (
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="2.8"
                  fill="none"
                  stroke={nodeColor}
                  strokeWidth="0.2"
                  opacity="0.5"
                  className="animate-ping origin-center"
                />
              )}
              {/* Main Node Circle */}
              <circle
                cx={node.x}
                cy={node.y}
                r={isSelected ? '2.4' : '1.8'}
                fill={nodeColor}
                stroke="#0f172a"
                strokeWidth="0.5"
                className="transition-all duration-200"
              />
              {/* Node ID label */}
              <text
                x={node.x}
                y={node.y - 2.8}
                textAnchor="middle"
                fontSize="2.2"
                fill={isSelected ? '#ffffff' : '#94a3b8'}
                fontWeight={isSelected ? 'bold' : 'normal'}
                className="pointer-events-none transition-colors"
              >
                {node.data.pharmacy_id}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Hover Info Card */}
      {hoveredNode && pharmacyCoords[hoveredNode] && (
        <div className="absolute bottom-4 right-4 z-10 p-3.5 rounded-xl bg-slate-900 border border-slate-700 text-xs backdrop-blur-md shadow-xl w-64 animate-in fade-in zoom-in-95 duration-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-mono text-emerald-400 font-bold">{hoveredNode}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
              {pharmacyCoords[hoveredNode].data.operating_status}
            </span>
          </div>
          <div className="font-bold text-white truncate">{pharmacyCoords[hoveredNode].data.pharmacy_name}</div>
          <div className="text-slate-400 text-[11px] mt-0.5">{pharmacyCoords[hoveredNode].data.city}</div>
          <div className="mt-2 pt-2 border-t border-slate-800 flex justify-between text-[11px]">
            <span className="text-slate-400">Capacity:</span>
            <span className="text-white font-mono">{pharmacyCoords[hoveredNode].data.storage_capacity.toLocaleString()} units</span>
          </div>
        </div>
      )}
    </div>
  );
};
