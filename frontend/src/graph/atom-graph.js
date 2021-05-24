import ForceGraph3D from '3d-force-graph';
import SpriteText from 'three-spritetext';
import home from './home.json';

class AtomGraph {

    constructor() {
        this.Graph = ForceGraph3D()(document.getElementById('graph_elem'))
          .nodeAutoColorBy('group')
          .nodeThreeObject(node => {
            const sprite = new SpriteText(node.name);
            sprite.material.depthWrite = false; // make sprite background transparent
            sprite.color = node.color;
            sprite.textHeight = 8;
            return sprite;
          })
          .nodeThreeObjectExtend(true)
          .nodeOpacity(.8)
          .nodeResolution(32);
  
      // Spread nodes a little wider
      this.Graph.d3Force('charge').strength(-120);
    }

    setHome() {

        // const gData = JSON.parse;
        this.Graph.graphData(home);
        // this.Graph.zoomToFit()
        const distance = 100;
    

        this.Graph.cameraPosition({ z: distance })
        this.Graph.onNodeClick(node => {
            const distance = 40;
            const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
  
            this.Graph.cameraPosition(
              { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
              node, // lookAt ({ x, y, z })
              3000  // ms transition duration
            );

                if (node.name === "Search") {
                    document.getElementById("searchToggle").dispatchEvent(new Event("click"));
            }
        }
        )
    }
        

}

export default AtomGraph