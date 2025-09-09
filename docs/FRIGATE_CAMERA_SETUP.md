# 📹 Frigate NVR Setup for Oliver's Vision System

## 🎯 **Objective: Give Oliver Eyes**

Add 4x Vimtag 847 PTZ cameras to provide Oliver with workshop awareness, object detection, and AI-driven triggers for n8n workflows.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   4x Cameras    │────│   Frigate NVR   │────│   n8n Workflows │
│   (Workshop)    │    │   (AI Vision)   │    │   (Triggers)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   (Events DB)   │
                       └─────────────────┘
```

## 📦 **Docker Integration**

### 1. Add to docker-compose.yml

```yaml
  frigate:
    image: ghcr.io/blakeblackshear/frigate:stable
    container_name: frigate
    hostname: frigate
    networks: ['demo']
    restart: unless-stopped
    ports:
      - "5000:5000"  # Web UI
      - "8554:8554"  # RTSP re-stream
      - "8555:8555/tcp" # WebRTC
      - "8555:8555/udp" # WebRTC
    environment:
      - FRIGATE_RTSP_PASSWORD=${FRIGATE_RTSP_PASSWORD}
    volumes:
      - ./config/frigate.yml:/config/config.yml:ro
      - ./data/frigate:/media/frigate
      - type: tmpfs # Optional: faster processing
        target: /tmp/cache
        tmpfs:
          size: 1000000000 # 1GB
    shm_size: "256mb" # Increase if multiple cameras
    devices:
      - /dev/dri:/dev/dri # For hardware acceleration
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia # GPU acceleration for detection
              count: 1
              capabilities: [gpu]
    profiles: ["cameras", "gpu-nvidia"]
```

### 2. Add to .env file

```bash
# Frigate Configuration
FRIGATE_RTSP_PASSWORD=your_camera_password
CAMERA_1_IP=192.168.1.101
CAMERA_2_IP=192.168.1.102
CAMERA_3_IP=192.168.1.103
CAMERA_4_IP=192.168.1.104
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_camera_password
```

## 🔧 **Frigate Configuration**

### Create: `config/frigate.yml`

```yaml
mqtt:
  # Optional: Enable for advanced automation
  enabled: false

database:
  path: /media/frigate/frigate.db

api:
  host: 0.0.0.0
  port: 5000

detectors:
  ov:
    type: openvino
    device: AUTO

model:
  path: /openvino-model/ssdlite_mobilenet_v2.xml
  input_tensor: nhwc
  input_pixel_format: bgr
  width: 300
  height: 300

# Define your 4 cameras
cameras:
  workshop_main:
    ffmpeg:
      inputs:
        - path: rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_1_IP}/stream1
          roles:
            - detect
            - record
        - path: rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_1_IP}/stream2
          roles:
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5
    record:
      enabled: true
      events:
        retain:
          default: 30 # days
          objects:
            person: 60
    objects:
      track:
        - person
        - car
        - truck
        - bicycle
      filters:
        person:
          min_area: 2000
          threshold: 0.7

  workshop_left:
    ffmpeg:
      inputs:
        - path: rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_2_IP}/stream1
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5
    record:
      enabled: true
    objects:
      track:
        - person
        - car

  workshop_right:
    ffmpeg:
      inputs:
        - path: rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_3_IP}/stream1
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5
    record:
      enabled: true
    objects:
      track:
        - person
        - car

  workshop_overview:
    ffmpeg:
      inputs:
        - path: rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_4_IP}/stream1
          roles:
            - detect
            - record
    detect:
      width: 1920
      height: 1080
      fps: 5
    record:
      enabled: true
    objects:
      track:
        - person
        - car
        - bicycle

# Motion detection zones (customize for your workshop)
motion:
  mask: ""
  improve_contrast: true
  threshold: 25
  contour_area: 30

go2rtc:
  streams:
    workshop_main: "rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_1_IP}/stream1"
    workshop_left: "rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_2_IP}/stream1"
    workshop_right: "rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_3_IP}/stream1"
    workshop_overview: "rtsp://{FRIGATE_RTSP_USER}:{FRIGATE_RTSP_PASSWORD}@{CAMERA_4_IP}/stream1"
```

## 🤖 **n8n Integration for Oliver**

### Webhook Triggers for Object Detection

Frigate can send webhooks to n8n for real-time events:

1. **Person Detection Workflow**:

   ```
   Frigate Webhook → Check Person Confidence → Capture Snapshot → 
   Send to Oliver → Generate Context-Aware Response
   ```

2. **Motion Alert Workflow**:

   ```
   Motion Detected → Check Time/Conditions → Send Alert to Oliver →
   Oliver Analyzes Scene → Appropriate Response
   ```

### Sample n8n Webhook URL

```
http://host.docker.internal:5678/webhook/frigate-detection
```

## 🎯 **Oliver's Workshop Awareness**

### Visual Context for AI

- **Person Detection**: "I see you're working on the lathe"
- **Tool Recognition**: "The drill press is running"
- **Safety Monitoring**: "Motion detected near hazardous equipment"
- **Inventory Tracking**: "New parts added to workbench"

### Integration with Speech

```
User: "Oliver, what's happening in the workshop?"
Oliver: "I can see you at the main workbench. The overhead light is on, and there are tools on the table. No other activity detected."
```

## 🚀 **Setup Steps**

### 1. Create Directory Structure

```powershell
mkdir -p config
mkdir -p data/frigate
```

### 2. Configure Cameras

```powershell
# Test camera connections first
curl "rtsp://admin:password@192.168.1.101/stream1"
```

### 3. Update docker-compose.yml

Add the Frigate service definition above.

### 4. Start Services

```powershell
# Start with cameras profile
docker compose --profile gpu-nvidia --profile cameras up -d

# Or start just frigate
docker compose up frigate -d
```

### 5. Access Web UI

- **Frigate Dashboard**: <http://localhost:5000>
- **Live Streams**: View all 4 cameras
- **Events**: AI-detected objects and motions

## 🔧 **Camera-Specific Configuration**

### Vimtag 847 PTZ Settings

```yaml
# For each camera, optimize settings:
detect:
  enabled: true
  width: 1920
  height: 1080
  fps: 5  # Start conservative, increase if needed

# PTZ controls (if supported)
onvif:
  host: {CAMERA_IP}
  port: 80
  user: {CAMERA_USERNAME}
  password: {CAMERA_PASSWORD}
```

## 📊 **Performance Monitoring**

### Resource Usage

```powershell
# Monitor Frigate performance
docker stats frigate

# Check detection accuracy
curl http://localhost:5000/api/stats
```

### GPU Utilization

```powershell
# Monitor GPU usage for detection
nvidia-smi

# Check if GPU acceleration is working
docker logs frigate | findstr "GPU"
```

## 🎯 **Next Steps After Camera Setup**

1. **Object Recognition Training**: Train custom models for workshop tools
2. **Safety Monitoring**: Alert workflows for dangerous situations  
3. **Inventory Tracking**: Visual recognition of parts and materials
4. **Time-lapse Creation**: Automatic project documentation
5. **Oliver Integration**: Real-time visual context for conversations

## 🔍 **Troubleshooting**

### Common Issues

- **Camera Connection**: Verify RTSP URLs and credentials
- **Performance**: Adjust detection FPS and resolution
- **Storage**: Monitor disk space in `./data/frigate`
- **GPU**: Ensure NVIDIA runtime is available

### Debug Commands

```powershell
# Test camera RTSP stream
ffplay "rtsp://admin:password@192.168.1.101/stream1"

# Check Frigate logs
docker logs frigate

# Verify GPU detection
docker exec frigate nvidia-smi
```

---

**🎯 This setup will give Oliver eyes to see the workshop and react intelligently to what's happening around you!**
