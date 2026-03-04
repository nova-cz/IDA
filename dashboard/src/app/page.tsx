"use client"

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  ZAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import data from '../data.json';

const COLORS = ['#2ecc71', '#e74c3c'];
const LINE_COLORS = { 'faciles': '#3498db', 'medios': '#f1c40f', 'dificiles': '#e74c3c' };

export default function Dashboard() {
  // Transform timeData
  const sizes = Array.from(new Set(data.timeData.map((d: any) => d.n_size)));
  const formattedTimeData = sizes.map(size => {
    const item: any = { n_size: size };
    data.timeData.forEach((d: any) => {
      if (d.n_size === size) {
        item[d.difficulty] = d.time_seconds;
      }
    });
    return item;
  });

  // Transform countData
  const formattedCountData = sizes.map(size => {
    const item: any = { n_size: size, 'Encontrada': 0, 'Timeout (Memoria Límite)': 0 };
    data.countData.forEach((d: any) => {
      if (d.n_size === size) {
        item[d.Estado] = d.Cantidad;
      }
    });
    return item;
  });

  // Transform nodesData
  const formattedNodesData = sizes.map(size => {
    const item: any = { n_size: size };
    data.nodesData?.forEach((d: any) => {
      if (d.n_size === size) {
        item[d.difficulty] = d.nodes_expanded;
      }
    });
    return item;
  });

  // Transform lengthData
  const formattedLengthData = sizes.map(size => {
    const item: any = { n_size: size };
    data.lengthData?.forEach((d: any) => {
      if (d.n_size === size) {
        item[d.difficulty] = d.solution_length;
      }
    });
    return item;
  });

  // Transform globalCounts
  const pieData = Object.keys(data.globalCounts).map(key => ({
    name: key,
    value: (data.globalCounts as any)[key],
    fill: key === 'Encontrada' ? COLORS[0] : COLORS[1]
  }));

  // Scatter split
  const scatterFaciles = (data as any).scatterData?.filter((d: any) => d.difficulty === 'faciles') || [];
  const scatterMedios = (data as any).scatterData?.filter((d: any) => d.difficulty === 'medios') || [];
  const scatterDificiles = (data as any).scatterData?.filter((d: any) => d.difficulty === 'dificiles') || [];

  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans text-slate-800">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">
            Análisis Empírico de Rendimiento: IDA* Híbrido (N-Puzzle)
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            Exploración visual del comportamiento asintótico y rotura matemática
          </p>
        </header>

        {/* Time Line Chart */}
        <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
          <h2 className="text-2xl font-bold mb-6 text-slate-800">
            Explosión Combinatoria: Crecimiento de Tiempo por Dimensión
          </h2>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={formattedTimeData} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="n_size" tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                <YAxis scale="log" domain={['auto', 'auto']} tickFormatter={(tick) => tick.toFixed(3)} tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                <Tooltip
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  labelStyle={{ fontWeight: 'bold', color: '#1E293B', marginBottom: '8px' }}
                  formatter={(value: any) => [`${Number(value).toFixed(4)}s`, 'Tiempo']}
                  labelFormatter={(label) => `Tamaño: ${label}x${label}`}
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                <Line type="monotone" dataKey="faciles" name="Fáciles" stroke={LINE_COLORS.faciles} strokeWidth={4} dot={{ r: 6, strokeWidth: 2 }} activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="medios" name="Medios" stroke={LINE_COLORS.medios} strokeWidth={4} dot={{ r: 6, strokeWidth: 2 }} activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="dificiles" name="Difíciles" stroke={LINE_COLORS.dificiles} strokeWidth={4} dot={{ r: 6, strokeWidth: 2 }} activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Nodes and Length Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
            <h2 className="text-xl font-bold mb-6 text-slate-800">
              Nodos Expandidos por Dimensión (Log)
            </h2>
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedNodesData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="n_size" tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                  <YAxis scale="log" domain={['auto', 'auto']} tickFormatter={(tick) => tick.toLocaleString()} tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(value: any) => [Math.round(Number(value)).toLocaleString(), 'Nodos']}
                    labelFormatter={(label) => `Tamaño: ${label}x${label}`}
                  />
                  <Legend iconType="circle" />
                  <Line type="monotone" dataKey="faciles" name="Fáciles" stroke={LINE_COLORS.faciles} strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="medios" name="Medios" stroke={LINE_COLORS.medios} strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="dificiles" name="Difíciles" stroke={LINE_COLORS.dificiles} strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
            <h2 className="text-xl font-bold mb-6 text-slate-800">
              Longitud de Solución por Dimensión
            </h2>
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedLengthData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="n_size" tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(value: any) => [Math.round(Number(value)), 'Movimientos']}
                    labelFormatter={(label) => `Tamaño: ${label}x${label}`}
                  />
                  <Legend iconType="circle" />
                  <Line type="monotone" dataKey="faciles" name="Fáciles" stroke={LINE_COLORS.faciles} strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="medios" name="Medios" stroke={LINE_COLORS.medios} strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="dificiles" name="Difíciles" stroke={LINE_COLORS.dificiles} strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Bar Chart */}
          <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
            <h2 className="text-xl font-bold mb-6 text-slate-800">
              Rotura de Rendimiento: Éxito vs Timeout
            </h2>
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={formattedCountData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="n_size" tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                  <Tooltip
                    cursor={{ fill: '#F1F5F9' }}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    labelFormatter={(label) => `Tamaño: ${label}x${label}`}
                  />
                  <Legend iconType="circle" />
                  <Bar dataKey="Encontrada" name="Encontrada" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Timeout (Memoria Límite)" name="Timeout" fill={COLORS[1]} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Pie Chart */}
          <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md flex flex-col">
            <h2 className="text-xl font-bold mb-2 text-slate-800">
              Proporción Global
            </h2>
            <div className="flex-1 w-full min-h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                    animationBegin={200}
                    animationDuration={1500}
                  />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(value: any, name: any) => [`${value} instancias`, name]}
                  />
                  <Legend iconType="circle" verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>

        {/* Scatter Chart - Individual Instance Cost */}
        <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md mt-8">
          <h2 className="text-2xl font-bold mb-6 text-slate-800">
            Costo Individual por Instancia (Menor a Mayor)
          </h2>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="index" type="number" name="Índice Global" tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                <YAxis dataKey="time_seconds" type="number" name="Tiempo (s)" tickFormatter={(tick) => tick.toFixed(2)} tickLine={false} axisLine={false} tick={{ fill: '#64748B' }} />
                <ZAxis dataKey="n_size" type="number" range={[40, 40]} name="Dimensión" />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  formatter={(value: any, name: any) => [name === 'Tiempo (s)' ? `${Number(value).toFixed(4)}s` : value, name]}
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                <Scatter name="Fáciles" data={scatterFaciles} fill={LINE_COLORS.faciles} />
                <Scatter name="Medios" data={scatterMedios} fill={LINE_COLORS.medios} />
                <Scatter name="Difíciles" data={scatterDificiles} fill={LINE_COLORS.dificiles} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </section>

      </div>
    </div>
  );
}
