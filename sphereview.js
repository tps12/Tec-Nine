import * as THREE from 'three';

const _yAxis = new THREE.Vector3(0, 1, 0);

function midpoint(buffer, face) {
  return new THREE.Vector3(
    (buffer.getX(face.a)+buffer.getX(face.b)+buffer.getX(face.c))/3,
    (buffer.getY(face.a)+buffer.getY(face.b)+buffer.getY(face.c))/3,
    (buffer.getZ(face.a)+buffer.getZ(face.b)+buffer.getZ(face.c))/3
  );
}

export default {
  template: '<div></div>',
  mounted() {
    const connectInterval = setInterval(() => {
      if (window.socket.id === undefined) return;
      this.$emit('mounted');
      clearInterval(connectInterval);
    }, 100);
  },
  methods: {
    initialize(vertices, normals) {
      const container = this.$el;

      const camera = new THREE.OrthographicCamera(-1.1, 1.1, 1.1, -1.1, 0, 11);
      camera.position.z = 11;

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x050505);

      const light = new THREE.HemisphereLight();
      light.intensity = 3;
      scene.add( light );

      this.geometry = new THREE.BufferGeometry();

      this.geometry.setAttribute('position', new THREE.Float32BufferAttribute( vertices, 3 ));
      this.geometry.setAttribute('normal', new THREE.Float32BufferAttribute( normals, 3 ));

      const material = new THREE.MeshPhongMaterial({side: THREE.FrontSide, vertexColors: true});

      this.mesh = new THREE.Mesh(this.geometry, material);
      scene.add(this.mesh);

      const renderer = new THREE.WebGLRenderer({antialias: true});
      renderer.setPixelRatio(window.devicePixelRatio);
      container.appendChild(renderer.domElement);

      renderer.domElement.addEventListener('click', (event) => {
        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(
          new THREE.Vector2((event.offsetX/event.srcElement.width) * 2 - 1,
                            -(event.offsetY/event.srcElement.height) * 2 + 1),
          camera);
        const intersect = raycaster.intersectObject(this.mesh, false)[0];
        if (intersect) {
          this.$emit('clicked', ...midpoint(this.geometry.attributes.position, intersect.face));
        }
      });

      this.paint = () => renderer.render(scene, camera);
      const resize = () => {
        const size = Math.min(window.innerWidth, window.innerHeight);
        renderer.setSize(size, size);
        this.paint();
      };
      window.addEventListener('resize', resize);
      resize();
    },

    setColors(colors) {
      this.geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      this.paint();
    },

    rotate(angle) {
      this.mesh.setRotationFromAxisAngle(_yAxis, angle);
      this.paint();
    }
  }
};

