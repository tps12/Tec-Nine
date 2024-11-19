import * as THREE from 'three';


export default {
  template: '<div></div>',
  mounted() {
/*  const container = this.$el;
			let camera, scene, renderer, stats;

			let mesh;

			init();

			function init() {

				//

				camera = new THREE.PerspectiveCamera( 27, window.innerWidth / window.innerHeight, 1, 3500 );
				camera.position.z = 64;

				scene = new THREE.Scene();
				scene.background = new THREE.Color( 0x050505 );

				//

				const light = new THREE.HemisphereLight();
				light.intensity = 3;
				scene.add( light );

				//

				const geometry = new THREE.BufferGeometry();

				const indices = [];

				const vertices = [];
				const normals = [];
				const colors = [];

				const size = 20;
				const segments = 10;

				const halfSize = size / 2;
				const segmentSize = size / segments;

				const _color = new THREE.Color();

				// generate vertices, normals and color data for a simple grid geometry

				for ( let i = 0; i <= segments; i ++ ) {

					const y = ( i * segmentSize ) - halfSize;

					for ( let j = 0; j <= segments; j ++ ) {

						const x = ( j * segmentSize ) - halfSize;

						vertices.push( x, - y, 0 );
						normals.push( 0, 0, 1 );

						const r = ( x / size ) + 0.5;
						const g = ( y / size ) + 0.5;

						_color.setRGB( r, g, 1, THREE.SRGBColorSpace );

						colors.push( _color.r, _color.g, _color.b );

					}

				}

				// generate indices (data for element array buffer)

				for ( let i = 0; i < segments; i ++ ) {

					for ( let j = 0; j < segments; j ++ ) {

						const a = i * ( segments + 1 ) + ( j + 1 );
						const b = i * ( segments + 1 ) + j;
						const c = ( i + 1 ) * ( segments + 1 ) + j;
						const d = ( i + 1 ) * ( segments + 1 ) + ( j + 1 );

						// generate two faces (triangles) per iteration

						indices.push( a, b, d ); // face one
						indices.push( b, c, d ); // face two

					}

				}

				//

				geometry.setIndex( indices );
				geometry.setAttribute( 'position', new THREE.Float32BufferAttribute( vertices, 3 ) );
				geometry.setAttribute( 'normal', new THREE.Float32BufferAttribute( normals, 3 ) );
				geometry.setAttribute( 'color', new THREE.Float32BufferAttribute( colors, 3 ) );

				const material = new THREE.MeshPhongMaterial( {
					side: THREE.DoubleSide,
					vertexColors: true
				} );

				mesh = new THREE.Mesh( geometry, material );
				scene.add( mesh );

				//

				renderer = new THREE.WebGLRenderer( { antialias: true } );
				renderer.setPixelRatio( window.devicePixelRatio );
				renderer.setSize( window.innerWidth, window.innerHeight );
				//renderer.setAnimationLoop( animate );
				container.appendChild( renderer.domElement );
renderer.render(scene, camera);

                }*/

      //


      //

    /*  window.addEventListener( 'resize', onWindowResize.bind(this) );
     this. renderer.render( this.scene,this.camera );*/

      const connectInterval = setInterval(() => {
        if (window.socket.id === undefined) return;
        this.$emit('init');
        clearInterval(connectInterval);
      }, 100);


    function onWindowResize() {

        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize( window.innerWidth, window.innerHeight );
        this.renderer.render( this.scene, this.camera );

    }
  },
  methods: {
    test(vertexValues, normalValues, colorValues) {//positions, normals, colors) {

    const container = this.$el;
/*
      this.camera = new THREE.PerspectiveCamera( 20, window.innerWidth / window.innerHeight, 1, 10000 );//THREE.OrthographicCamera(-1.1, 1.1, 1.1, -1.1, 0, 11);
      this.camera.position.z = 11;

      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color( 0x050505 );
      //this.scene.fog = new THREE.Fog( 0x050505, 2000, 3500 );

      //this.scene.add( new THREE.AmbientLight( 0x00ffff, 0.25 ) );

      const light1 = new THREE.DirectionalLight( 0x00ffff, 1.5 );
      light1.position.set( 1, 1, 1 );
      this.scene.add( light1 );

//      const light2 = new THREE.DirectionalLight( 0xffffff, 4.5 );
//      light2.position.set( 0, - 1, 0 );
//      this.scene.add( light2 );

      const triangles = 16000;

      this.geometry = new THREE.BufferGeometry();

      function disposeArray() {
        this.array = null;
      }
      const color = new THREE.Color();
      const colorValues = [];
      for (let i = 0; i < colors.length; i += 4) {
        color.setRGB(colors[i], colors[i+1], colors[i+2], THREE.SRGBColorSpace);
        colorValues.push(color.r, color.g, color.b);     
      }

      this.geometry.setAttribute( 'position', new THREE.Float32BufferAttribute( positions, 3 ).onUpload( disposeArray ) );
      this.geometry.setAttribute( 'normal', new THREE.Float32BufferAttribute( normals, 3 ).onUpload( disposeArray ) );
      this.geometry.setAttribute( 'color', new THREE.Float32BufferAttribute( colorValues, 3 ).onUpload( disposeArray ) );

      this.geometry.computeBoundingSphere();

      const material = new THREE.MeshPhongMaterial( {
              side: THREE.DoubleSide, vertexColors: true
      } );

      this.mesh = new THREE.Mesh( this.geometry, this.material );
      this.scene.add( this.mesh );

      //

      this.renderer = new THREE.WebGLRenderer( { antialias: true } );
      this.renderer.setPixelRatio( window.devicePixelRatio );
      this.renderer.setSize( window.innerWidth, window.innerHeight );
      //renderer.setAnimationLoop( animate );
      container.appendChild( this.renderer.domElement );


     // this.geometry.setAttribute( 'color', new THREE.Float32BufferAttribute( colors, 4 ).onUpload( disposeArray ) );
      //this.geometry.attributes.color.needsUpdate = true;
      this.renderer.render( this.scene, this.camera );*/
console.log(vertexValues.length);
let camera, scene, renderer, mesh;
				camera = new THREE.PerspectiveCamera( 10, window.innerWidth / window.innerHeight, 1, 100);
//camera = new THREE.OrthographicCamera(-1.1, 1.1, 1.1, -1.1, 0, 11);
      camera.position.z = 20;

				scene = new THREE.Scene();
				scene.background = new THREE.Color( 0x050505 );

				//

				const light = new THREE.HemisphereLight();
				light.intensity = 3;
				scene.add( light );

				//

				const geometry = new THREE.BufferGeometry();

				const indices = [];

				const vertices = [];
				const normals = [];
				const colors = [];

				const size = 20;
				const segments = 10;

				const halfSize = size / 2;
				const segmentSize = size / segments;

				const _color = new THREE.Color();

				// generate vertices, normals and color data for a simple grid geometry

				for ( let i = 0; i <= segments; i ++ ) {

					const y = ( i * segmentSize ) - halfSize;

					for ( let j = 0; j <= segments; j ++ ) {

						const x = ( j * segmentSize ) - halfSize;

						vertices.push( x, - y, 0 );
						normals.push( 0, 0, 1 );

						const r = ( x / size ) + 0.5;
						const g = ( y / size ) + 0.5;

						_color.setRGB( r, g, 1, THREE.SRGBColorSpace );

						colors.push( _color.r, _color.g, _color.b );

					}

				}

				// generate indices (data for element array buffer)

				for ( let i = 0; i < segments; i ++ ) {

					for ( let j = 0; j < segments; j ++ ) {

						const a = i * ( segments + 1 ) + ( j + 1 );
						const b = i * ( segments + 1 ) + j;
						const c = ( i + 1 ) * ( segments + 1 ) + j;
						const d = ( i + 1 ) * ( segments + 1 ) + ( j + 1 );

						// generate two faces (triangles) per iteration

						indices.push( a, b, d ); // face one
						indices.push( b, c, d ); // face two

					}

				}

				//

				//geometry.setIndex( indices );
				geometry.setAttribute( 'position', new THREE.Float32BufferAttribute( vertexValues, 3 ) );
				geometry.setAttribute( 'normal', new THREE.Float32BufferAttribute( normalValues, 3 ) );
				geometry.setAttribute( 'color', new THREE.Float32BufferAttribute( colorValues, 3 ) );

				const material = new THREE.MeshPhongMaterial( {
					side: THREE.DoubleSide,
					vertexColors: true
				} );

				mesh = new THREE.Mesh( geometry, material );
				scene.add( mesh );

				//

				renderer = new THREE.WebGLRenderer( { antialias: true } );
				renderer.setPixelRatio( window.devicePixelRatio );
				renderer.setSize( window.innerWidth, window.innerHeight );
				container.appendChild( renderer.domElement );
renderer.render(scene, camera);
    },
  }
};

