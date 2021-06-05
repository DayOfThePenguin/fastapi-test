import React from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import SpriteText from 'three-spritetext';

import theme from '../theme';
import home from '../home.json';

const { useRef, useCallback } = React;

const GraphView = () => {
    const fgRef = useRef();
    const handleClick = useCallback(node => {
        // Aim at node from outside it
        const distance = 40;
        const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

        fgRef.current.cameraPosition(
            { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
            node, // lookAt ({ x, y, z })
            3000  // ms transition duration
        );
    }, [fgRef]);

    const createNodeThreeObject = (node) => {
        const sprite = new SpriteText(node.name);
        sprite.material.depthWrite = false; // make sprite background transparent
        sprite.color = node.color;
        sprite.textHeight = 8;
        return sprite;
    }

    const backgroundColor = theme.palette.background.default;
    const graphData = home;
    return (
        <ForceGraph3D
            ref={fgRef}
            onNodeClick={handleClick}
            backgroundColor={backgroundColor}
            graphData={graphData}
            nodeThreeObject={createNodeThreeObject}
            nodeThreeObjectExtend={true}
            nodeOpacity={0.6}
            d3VelocityDecay={.55}
            nodeResolution={32}
        />
    )
}

export default GraphView;