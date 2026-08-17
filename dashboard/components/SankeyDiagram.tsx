'use client';
import { ResponsiveSankey } from '@nivo/sankey';

interface SankeyNode {
  id: string;
}

interface SankeyLink {
  source: string;
  target: string;
  value: number;
}

interface SankeyDiagramProps {
  nodes: SankeyNode[];
  links: SankeyLink[];
  height?: number;
}

/**
 * SankeyDiagram — Nivo ResponsiveSankey wrapped with dark-theme styling.
 * Used for Q6: showing information-seeking flows (Myntra → external platform → outcome).
 */
export default function SankeyDiagram({ nodes, links, height = 360 }: SankeyDiagramProps) {
  if (!nodes || nodes.length === 0 || !links || links.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🌊</div>
        <div className="empty-state-text">No flow data available</div>
      </div>
    );
  }

  return (
    <div style={{ height, width: '100%' }}>
      <ResponsiveSankey
        data={{ nodes, links }}
        margin={{ top: 16, right: 120, bottom: 16, left: 120 }}
        align="justify"
        colors={[
          '#ff3f6c', '#ff7849', '#a855f7', '#2dd4bf',
          '#3b82f6', '#fbbf24', '#ec4899', '#84cc16',
        ]}
        nodeOpacity={1}
        nodeHoverOpacity={1}
        nodeThickness={18}
        nodeSpacing={20}
        nodeBorderWidth={0}
        nodeBorderRadius={4}
        linkOpacity={0.25}
        linkHoverOpacity={0.55}
        linkContract={2}
        enableLinkGradient={true}
        labelPosition="outside"
        labelOrientation="horizontal"
        labelPadding={12}
        labelTextColor={{ from: 'color', modifiers: [['brighter', 2]] }}
        theme={{
          text: { fill: 'rgba(255,255,255,0.65)', fontSize: 12 },
          tooltip: {
            container: {
              background: '#13131f',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 8,
              fontSize: 12,
              color: 'rgba(255,255,255,0.9)',
            },
          },
        }}
      />
    </div>
  );
}
