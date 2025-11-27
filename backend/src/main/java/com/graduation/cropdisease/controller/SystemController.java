package com.graduation.cropdisease.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.graduation.cropdisease.service.SystemService;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/system")
@CrossOrigin(origins = "*")
public class SystemController {
    
    @Autowired
    private SystemService systemService;
    
    /**
     * 系统健康检查
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> response = new HashMap<>();
        try {
            // 检查各个组件状态
            boolean yoloServiceStatus = systemService.checkYoloService();
            boolean databaseStatus = systemService.checkDatabase();
            
            response.put("status", "healthy");
            response.put("timestamp", System.currentTimeMillis());
            response.put("services", Map.of(
                "yolo", yoloServiceStatus ? "running" : "stopped",
                "database", databaseStatus ? "connected" : "disconnected",
                "backend", "running"
            ));
            response.put("message", "作物病害检测系统运行正常");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("status", "error");
            response.put("message", "系统检查失败: " + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * 获取系统信息
     */
    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> getSystemInfo() {
        Map<String, Object> response = new HashMap<>();
        response.put("name", "作物病害智能检测系统");
        response.put("version", "1.0.0");
        response.put("description", "基于YOLO的作物病害智能识别与治疗建议系统");
        response.put("author", "毕业设计项目");
        response.put("features", new String[]{
            "智能病害识别",
            "治疗方案推荐", 
            "检测历史记录",
            "用户管理"
        });
        response.put("supportedCrops", new String[]{
            "苹果", "番茄", "玉米", "葡萄", "土豆", 
            "樱桃", "草莓", "大豆", "南瓜", "树莓"
        });
        return ResponseEntity.ok(response);
    }
    
    /**
     * 重启YOLO服务
     */
    @PostMapping("/restart-yolo")
    public ResponseEntity<Map<String, Object>> restartYoloService() {
        Map<String, Object> response = new HashMap<>();
        try {
            boolean success = systemService.restartYoloService();
            if (success) {
                response.put("success", true);
                response.put("message", "YOLO服务重启成功");
            } else {
                response.put("success", false);
                response.put("message", "YOLO服务重启失败");
            }
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "重启失败: " + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }
}
