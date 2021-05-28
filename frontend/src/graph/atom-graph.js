import * as THREE from 'three';
import ForceGraph3D from '3d-force-graph';
import SpriteText from 'three-spritetext';


class AtomGraph {

  constructor() {
    this.Graph = ForceGraph3D()(document.getElementById('graph_elem'))
      .nodeAutoColorBy('group')
      .nodeThreeObject(node => {
        if (node.name === "WikiMap") {
          const imgTexture = new THREE.TextureLoader().load(`/static/img/wikimap.png`);
          const material = new THREE.SpriteMaterial({
            map: imgTexture
          });
          const sprite = new THREE.Sprite(material);
          sprite.scale.set(50, 14);
          return sprite;
        } else {
          const sprite = new SpriteText(node.name);
          sprite.material.depthWrite = false; // make sprite background transparent
          sprite.color = node.color;
          sprite.textHeight = 8;
          return sprite;
        }
      })
      .nodeThreeObjectExtend(node => {
        if (node.name === "WikiMap") {
          return false;
        } else {
          return true;
        }
      })
      .nodeOpacity(.8)
      .nodeResolution(32);

    // Spread nodes a little wider
    this.Graph.d3Force('charge').strength(-120);

    var loc = window.location,
      new_uri;
    if (loc.protocol === "https:") {
      new_uri = "wss:";
    } else {
      new_uri = "ws:";
    }
    new_uri += "//" + loc.host;
    new_uri += "/ws";


    var ws = new WebSocket(new_uri);

    ws.onmessage = (event) =>  {
      const jsonMessage = JSON.parse(event.data);
      const newNodes = jsonMessage.nodes;
      const newLinks = jsonMessage.links;
      console.log(newNodes);
      console.log(newLinks);
      const {
          nodes,
          links
      } = this.Graph.graphData();

      this.Graph.graphData({
          nodes: [...nodes, ...newNodes],
          links: [...links, ...newLinks]
      });
    }
    console.log(ws);
  }

  setHome() {
    const distance = 100;
    this.Graph.cameraPosition({
      z: distance
    })
    this.Graph.onNodeClick(node => {
      const distance = 40;
      const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
      this.Graph.cameraPosition({
          x: node.x * distRatio,
          y: node.y * distRatio,
          z: node.z * distRatio
        }, // new position
        node, // lookAt ({ x, y, z })
        3000 // ms transition duration
      );
      if (node.name === "Search") {
        document.getElementById("searchToggle").dispatchEvent(new Event("click"));
      }
      if (node.name === "GitHub") {
        window.open("https://github.com/DayOfThePenguin/r3th.ink");
      }
      if (node.name === "Bug Reports") {
        window.open("https://github.com/DayOfThePenguin/r3th.ink/issues");
      }
    });
  }

}


export default AtomGraph