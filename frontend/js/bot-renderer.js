/**
 * BotRenderer - 3D Bot Character using Three.js
 * Animated trading bot that reacts to market data
 */

class BotRenderer {
    constructor(canvasElement) {
        this.canvas = canvasElement;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.bot = null;
        
        this.animationState = 'idle';
        this.animationProgress = 0;
        
        this.init();
    }
    
    init() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a1428);
        
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.canvas.clientWidth / this.canvas.clientHeight,
            0.1,
            1000
        );
        this.camera.position.z = 3;
        
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: this.canvas, 
            antialias: true,
            alpha: true 
        });
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        
        this.setupLights();
        this.createBot();
        
        window.addEventListener('resize', () => this.onWindowResize());
        this.animate();
    }
    
    setupLights() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0x00ff96, 0.8);
        directionalLight.position.set(5, 8, 5);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);
        
        const pointLight = new THREE.PointLight(0x0099ff, 0.5);
        pointLight.position.set(-5, 3, 5);
        this.scene.add(pointLight);
    }
    
    createBot() {
        this.bot = new THREE.Group();
        
        // Head
        const headGeometry = new THREE.SphereGeometry(0.6, 32, 32);
        const headMaterial = new THREE.MeshStandardMaterial({
            color: 0x00ff96,
            metalness: 0.3,
            roughness: 0.4,
            emissive: 0x003d2d,
            emissiveIntensity: 0.3
        });
        this.bot.head = new THREE.Mesh(headGeometry, headMaterial);
        this.bot.head.position.y = 1;
        this.bot.head.castShadow = true;
        this.bot.add(this.bot.head);
        
        // Body
        const bodyGeometry = new THREE.BoxGeometry(0.8, 1.2, 0.5);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x1a3d3d,
            metalness: 0.5,
            roughness: 0.3,
            emissive: 0x003d2d,
            emissiveIntensity: 0.2
        });
        this.bot.body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        this.bot.body.castShadow = true;
        this.bot.add(this.bot.body);
        
        // Eyes
        const eyeGeometry = new THREE.SphereGeometry(0.15, 16, 16);
        const eyeMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            emissive: 0x00ff96,
            emissiveIntensity: 0.8
        });
        
        this.bot.eyeLeft = new THREE.Mesh(eyeGeometry, eyeMaterial);
        this.bot.eyeLeft.position.set(-0.2, 1.3, 0.45);
        this.bot.eyeLeft.castShadow = true;
        this.bot.add(this.bot.eyeLeft);
        
        this.bot.eyeRight = new THREE.Mesh(eyeGeometry, eyeMaterial.clone());
        this.bot.eyeRight.position.set(0.2, 1.3, 0.45);
        this.bot.eyeRight.castShadow = true;
        this.bot.add(this.bot.eyeRight);
        
        // Mouth
        const mouthGeometry = new THREE.BoxGeometry(0.4, 0.05, 0.05);
        const mouthMaterial = new THREE.MeshStandardMaterial({
            color: 0x00ff96,
            emissive: 0x00ff96,
            emissiveIntensity: 0.6
        });
        this.bot.mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
        this.bot.mouth.position.set(0, 0.9, 0.55);
        this.bot.mouth.castShadow = true;
        this.bot.add(this.bot.mouth);
        
        // Antenna
        const antennaGeometry = new THREE.CylinderGeometry(0.05, 0.05, 0.6, 8);
        const antennaMaterial = new THREE.MeshStandardMaterial({
            color: 0x0099ff,
            metalness: 0.8,
            roughness: 0.2,
            emissive: 0x0099ff,
            emissiveIntensity: 0.5
        });
        this.bot.antenna = new THREE.Mesh(antennaGeometry, antennaMaterial);
        this.bot.antenna.position.set(0, 1.6, 0);
        this.bot.antenna.castShadow = true;
        this.bot.add(this.bot.antenna);
        
        // Antenna tip
        const antennaTipGeometry = new THREE.SphereGeometry(0.08, 16, 16);
        const antennaTipMaterial = new THREE.MeshStandardMaterial({
            color: 0x0099ff,
            emissive: 0x0099ff,
            emissiveIntensity: 0.8
        });
        this.bot.antennaTip = new THREE.Mesh(antennaTipGeometry, antennaTipMaterial);
        this.bot.antennaTip.position.set(0, 2.1, 0);
        this.bot.antennaTip.castShadow = true;
        this.bot.add(this.bot.antennaTip);
        
        // Arms
        const armGeometry = new THREE.BoxGeometry(0.2, 0.8, 0.2);
        const armMaterial = new THREE.MeshStandardMaterial({
            color: 0x00d4aa,
            metalness: 0.4,
            roughness: 0.5
        });
        
        this.bot.armLeft = new THREE.Mesh(armGeometry, armMaterial);
        this.bot.armLeft.position.set(-0.7, 0.5, 0);
        this.bot.armLeft.castShadow = true;
        this.bot.add(this.bot.armLeft);
        
        this.bot.armRight = new THREE.Mesh(armGeometry, armMaterial.clone());
        this.bot.armRight.position.set(0.7, 0.5, 0);
        this.bot.armRight.castShadow = true;
        this.bot.add(this.bot.armRight);
        
        this.scene.add(this.bot);
    }
    
    setAnimationState(state) {
        this.animationState = state;
        this.animationProgress = 0;
    }
    
    updateAnimation() {
        this.animationProgress += 0.016;
        
        switch(this.animationState) {
            case 'idle':
                this.animateIdle();
                break;
            case 'thinking':
                this.animateThinking();
                break;
            case 'explaining':
                this.animateExplaining();
                break;
            case 'excited':
                this.animateExcited();
                break;
            case 'worried':
                this.animateWorried();
                break;
        }
    }
    
    animateIdle() {
        const sway = Math.sin(this.animationProgress * 2) * 0.15;
        this.bot.head.rotation.z = sway * 0.2;
        
        const blinkCycle = (this.animationProgress % 3) / 3;
        if (blinkCycle > 0.6 && blinkCycle < 0.65) {
            const blinkAmount = Math.abs((blinkCycle - 0.625) / 0.025);
            this.bot.eyeLeft.scale.y = Math.max(0.1, 1 - blinkAmount);
            this.bot.eyeRight.scale.y = Math.max(0.1, 1 - blinkAmount);
        } else {
            this.bot.eyeLeft.scale.y = 1;
            this.bot.eyeRight.scale.y = 1;
        }
    }
    
    animateThinking() {
        const tilt = Math.sin(this.animationProgress * 3) * 0.3;
        this.bot.head.rotation.z = tilt;
        
        const pulse = 1 + Math.sin(this.animationProgress * 4) * 0.1;
        this.bot.antenna.scale.y = pulse;
        this.bot.antennaTip.scale.set(pulse * 1.2, pulse * 1.2, pulse * 1.2);
        
        this.bot.eyeLeft.scale.y = 0.7;
        this.bot.eyeRight.scale.y = 0.7;
    }
    
    animateExplaining() {
        const armSwing = Math.sin(this.animationProgress * 4) * 0.4;
        this.bot.armLeft.rotation.z = armSwing;
        this.bot.armRight.rotation.z = -armSwing;
        
        const nodding = Math.sin(this.animationProgress * 3) * 0.2;
        this.bot.head.rotation.x = nodding;
        
        const talkingCycle = (this.animationProgress * 5) % 1;
        this.bot.mouth.scale.y = 0.8 + Math.sin(talkingCycle * Math.PI) * 0.4;
    }
    
    animateExcited() {
        const bounce = Math.abs(Math.sin(this.animationProgress * 5)) * 0.3;
        this.bot.position.y = bounce;
        
        this.bot.armLeft.rotation.z += 0.1;
        this.bot.armRight.rotation.z -= 0.1;
        
        this.bot.antenna.rotation.z = Math.sin(this.animationProgress * 6) * 0.3;
        
        this.bot.eyeLeft.scale.y = 1.3;
        this.bot.eyeRight.scale.y = 1.3;
    }
    
    animateWorried() {
        const fidget = Math.sin(this.animationProgress * 6) * 0.1;
        this.bot.body.rotation.z = fidget;
        
        const shake = Math.sin(this.animationProgress * 5) * 0.3;
        this.bot.head.rotation.y = shake;
        
        this.bot.eyeLeft.scale.y = 0.6;
        this.bot.eyeRight.scale.y = 0.6;
        
        this.bot.antenna.rotation.x = 0.3;
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        this.updateAnimation();
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
}
