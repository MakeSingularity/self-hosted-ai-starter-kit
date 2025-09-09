# 📹 Camera Setup and Testing Guide

## 🎯 **First Steps: Get Your Cameras Ready**

### 1. **Find Your Camera IPs**

Run this to scan your network for cameras:

```powershell
# Scan local network for cameras (adjust IP range as needed)
1..254 | ForEach-Object {
    $ip = "192.168.1.$_"
    if (Test-Connection -ComputerName $ip -Count 1 -Quiet) {
        Write-Host "Device found at: $ip" -ForegroundColor Green
    }
}
```

### 2. **Test Camera RTSP Streams**

Before starting Frigate, verify your cameras work:

```powershell
# Test each camera (replace with your actual IPs and credentials)
$cameras = @(
    "192.168.1.101",
    "192.168.1.102", 
    "192.168.1.103",
    "192.168.1.104"
)

foreach ($camera in $cameras) {
    Write-Host "Testing camera at $camera..." -ForegroundColor Yellow
    
    # Try common RTSP paths for Vimtag cameras
    $rtspUrls = @(
        "rtsp://admin:password@$camera/stream1",
        "rtsp://admin:password@$camera/cam/realmonitor?channel=1&subtype=0",
        "rtsp://admin:password@$camera/onvif1",
        "rtsp://admin:password@$camera/1"
    )
    
    foreach ($url in $rtspUrls) {
        Write-Host "  Trying: $url"
        # Use ffprobe to test stream (requires ffmpeg installed)
        # ffprobe -i $url -v quiet -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0
    }
}
```

### 3. **Configure Your .env File**

Update these values in your `.env` file:

```bash
# Replace with your actual camera credentials
FRIGATE_RTSP_USER=admin
FRIGATE_RTSP_PASSWORD=your_actual_password

# Replace with your discovered camera IPs
CAMERA_1_IP=192.168.1.101  # Workshop Main
CAMERA_2_IP=192.168.1.102  # Workshop Left  
CAMERA_3_IP=192.168.1.103  # Workshop Right
CAMERA_4_IP=192.168.1.104  # Workshop Overview
```

### 4. **Start Frigate**

```powershell
# Start Frigate along with your existing services
docker compose --profile gpu-nvidia --profile cameras up -d

# Or start just Frigate to test
docker compose up frigate -d
```

### 5. **Access Frigate Dashboard**

Open your browser to: <http://localhost:5000>

You should see:

- ✅ All 4 camera feeds
- ✅ Live object detection
- ✅ Event recordings
- ✅ System stats

## 🔧 **Common Vimtag 847 RTSP URLs**

Try these RTSP stream formats for your cameras:

```bash
# Primary stream (high quality)
rtsp://admin:password@IP/stream1
rtsp://admin:password@IP/cam/realmonitor?channel=1&subtype=0

# Secondary stream (lower quality, faster)  
rtsp://admin:password@IP/stream2
rtsp://admin:password@IP/cam/realmonitor?channel=1&subtype=1

# ONVIF streams
rtsp://admin:password@IP/onvif1
rtsp://admin:password@IP/onvif2
```

## 🚨 **Troubleshooting**

### Camera Not Connecting

1. **Check IP**: Use camera manufacturer app to find IP
2. **Test Credentials**: Try default admin/admin or admin/password
3. **Test RTSP**: Use VLC to test stream manually
4. **Check Firewall**: Ensure port 554 (RTSP) is open

### Frigate Issues

```powershell
# Check Frigate logs
docker logs frigate

# Check if GPU is detected
docker logs frigate | findstr "GPU"

# Test configuration syntax
docker exec frigate python -m frigate.config
```

### Performance Issues

1. **Reduce FPS**: Lower fps in config (start with 3-5)
2. **Lower Resolution**: Use stream2 instead of stream1
3. **Increase Memory**: Adjust shm_size in docker-compose.yml

## 🎯 **Oliver Integration Workflow**

Once cameras are working, create this n8n workflow:

```
Frigate Webhook → Check Event Type → Process Detection → 
Send to Oliver → Generate Response → Store Context
```

### Webhook URL for n8n

```
http://host.docker.internal:5678/webhook/oliver-vision
```

Add this to your Frigate config to send events to Oliver:

```yaml
# Add to frigate.yml
notifications:
  - platform: webhook
    url: "http://host.docker.internal:5678/webhook/oliver-vision"
    events:
      - person_entered_zone
      - person_left_zone
      - object_detected
```

---

**🎯 Ready to give Oliver eyes! Start with step 1 to find your cameras, then work through the setup.**
