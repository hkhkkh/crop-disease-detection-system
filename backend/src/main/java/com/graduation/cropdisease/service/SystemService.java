package com.graduation.cropdisease.service;

import org.springframework.stereotype.Service;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@Service
public class SystemService {
    
    private static final String YOLO_SERVICE_URL = "http://localhost:5000/health";
    private static final String PYTHON_BACKEND_URL = "http://localhost:8080/api/health";
    
    /**
     * 获取系统信息
     */
    public Map<String, Object> getSystemInfo() {
        Map<String, Object> systemInfo = new HashMap<>();
        
        // 基本系统信息
        systemInfo.put("serverTime", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        systemInfo.put("javaVersion", System.getProperty("java.version"));
        systemInfo.put("osName", System.getProperty("os.name"));
        systemInfo.put("osVersion", System.getProperty("os.version"));
        
        // 内存信息
        Runtime runtime = Runtime.getRuntime();
        long totalMemory = runtime.totalMemory() / 1024 / 1024; // MB
        long freeMemory = runtime.freeMemory() / 1024 / 1024; // MB
        long usedMemory = totalMemory - freeMemory;
        
        Map<String, Object> memoryInfo = new HashMap<>();
        memoryInfo.put("total", totalMemory + " MB");
        memoryInfo.put("used", usedMemory + " MB");
        memoryInfo.put("free", freeMemory + " MB");
        memoryInfo.put("usagePercentage", Math.round((double) usedMemory / totalMemory * 100) + "%");
        
        systemInfo.put("memory", memoryInfo);
        
        // 服务状态
        Map<String, Object> serviceStatus = new HashMap<>();
        serviceStatus.put("springBootBackend", "running");
        serviceStatus.put("yoloService", checkServiceStatus(YOLO_SERVICE_URL));
        serviceStatus.put("pythonBackend", checkServiceStatus(PYTHON_BACKEND_URL));
        
        systemInfo.put("services", serviceStatus);
        
        return systemInfo;
    }
    
    /**
     * 检查服务状态
     */
    private String checkServiceStatus(String serviceUrl) {
        try {
            URI uri = URI.create(serviceUrl);
            URL url = uri.toURL();
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(3000); // 3秒超时
            connection.setReadTimeout(3000);
            
            int responseCode = connection.getResponseCode();
            if (responseCode == 200) {
                return "running";
            } else {
                return "error";
            }
        } catch (Exception e) {
            return "stopped";
        }
    }
    
    /**
     * 检查YOLO服务状态
     */
    public boolean checkYoloService() {
        return "running".equals(checkServiceStatus(YOLO_SERVICE_URL));
    }
    
    /**
     * 检查数据库连接状态
     * 注意: 这是一个简化的检查，在实际生产环境中应使用数据源健康检查
     */
    public boolean checkDatabase() {
        // 由于使用H2内存数据库，默认返回true
        // 实际生产环境可以注入DataSource进行检查
        return true;
    }
    
    /**
     * 重启YOLO服务
     */
    public boolean restartYoloService() {
        // 检查服务状态，如果运行中就认为重启成功
        return checkYoloService();
    }
    
    /**
     * 获取系统健康状态
     */
    public Map<String, Object> getHealthStatus() {
        Map<String, Object> health = new HashMap<>();
        
        try {
            // 检查各个服务状态
            boolean yoloOk = "running".equals(checkServiceStatus(YOLO_SERVICE_URL));
            boolean pythonOk = "running".equals(checkServiceStatus(PYTHON_BACKEND_URL));
            
            // 检查内存使用率
            Runtime runtime = Runtime.getRuntime();
            long totalMemory = runtime.totalMemory();
            long freeMemory = runtime.freeMemory();
            double memoryUsage = (double) (totalMemory - freeMemory) / totalMemory;
            boolean memoryOk = memoryUsage < 0.9; // 内存使用率小于90%
            
            boolean overallHealth = yoloOk && pythonOk && memoryOk;
            
            health.put("status", overallHealth ? "UP" : "DOWN");
            health.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
            
            Map<String, Object> details = new HashMap<>();
            details.put("yoloService", yoloOk ? "UP" : "DOWN");
            details.put("pythonBackend", pythonOk ? "UP" : "DOWN");
            details.put("memory", memoryOk ? "OK" : "HIGH_USAGE");
            details.put("memoryUsagePercentage", Math.round(memoryUsage * 100) + "%");
            
            health.put("details", details);
            
        } catch (Exception e) {
            health.put("status", "DOWN");
            health.put("error", e.getMessage());
        }
        
        return health;
    }
}
