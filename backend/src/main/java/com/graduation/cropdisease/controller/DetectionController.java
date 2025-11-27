package com.graduation.cropdisease.controller;

import com.graduation.cropdisease.entity.DetectionRecord;
import com.graduation.cropdisease.entity.User;
import com.graduation.cropdisease.service.DetectionService;
import com.graduation.cropdisease.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/detections")
@CrossOrigin(origins = "*")
public class DetectionController {
    
    @Autowired
    private DetectionService detectionService;
    
    @Autowired
    private UserService userService;
    
    /**
     * 获取所有检测记录
     */
    @GetMapping
    public ResponseEntity<List<DetectionRecord>> getAllDetections() {
        List<DetectionRecord> records = detectionService.findAllRecords();
        return ResponseEntity.ok(records);
    }
    
    /**
     * 根据ID获取检测记录
     */
    @GetMapping("/{id}")
    public ResponseEntity<DetectionRecord> getDetectionById(@PathVariable Long id) {
        Optional<DetectionRecord> record = detectionService.findById(id);
        return record.map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * 根据用户ID获取检测记录
     */
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<DetectionRecord>> getDetectionsByUserId(@PathVariable Long userId) {
        List<DetectionRecord> records = detectionService.findByUserId(userId);
        return ResponseEntity.ok(records);
    }
    
    /**
     * 获取最近的检测记录
     */
    @GetMapping("/recent")
    public ResponseEntity<List<DetectionRecord>> getRecentDetections() {
        List<DetectionRecord> records = detectionService.getRecentDetections();
        return ResponseEntity.ok(records);
    }
    
    /**
     * 获取用户最近的检测记录
     */
    @GetMapping("/user/{userId}/recent")
    public ResponseEntity<List<DetectionRecord>> getUserRecentDetections(@PathVariable Long userId,
                                                                       @RequestParam(defaultValue = "10") int limit) {
        List<DetectionRecord> records = detectionService.getUserRecentDetections(userId, limit);
        return ResponseEntity.ok(records);
    }
    
    /**
     * 创建检测记录
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createDetection(@RequestBody Map<String, Object> detectionData) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            Long userId = Long.valueOf(detectionData.get("userId").toString());
            String imagePath = (String) detectionData.get("imagePath");
            String detectedDisease = (String) detectionData.get("detectedDisease");
            Double confidence = Double.valueOf(detectionData.get("confidence").toString());
            String recommendations = (String) detectionData.get("recommendations");
            
            Optional<User> userOpt = userService.findById(userId);
            if (userOpt.isEmpty()) {
                response.put("success", false);
                response.put("message", "用户不存在");
                return ResponseEntity.badRequest().body(response);
            }
            
            DetectionRecord record = detectionService.saveDetectionResult(
                userOpt.get(), imagePath, detectedDisease, confidence, recommendations
            );
            
            response.put("success", true);
            response.put("message", "检测记录创建成功");
            response.put("record", record);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "创建检测记录失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 根据疾病类型获取记录
     */
    @GetMapping("/disease/{diseaseType}")
    public ResponseEntity<List<DetectionRecord>> getDetectionsByDiseaseType(@PathVariable String diseaseType) {
        List<DetectionRecord> records = detectionService.findByDiseaseType(diseaseType);
        return ResponseEntity.ok(records);
    }
    
    /**
     * 根据置信度范围获取记录
     */
    @GetMapping("/confidence")
    public ResponseEntity<List<DetectionRecord>> getDetectionsByConfidence(
            @RequestParam Double minConfidence,
            @RequestParam Double maxConfidence) {
        List<DetectionRecord> records = detectionService.findByConfidenceRange(minConfidence, maxConfidence);
        return ResponseEntity.ok(records);
    }
    
    /**
     * 获取高置信度检测结果
     */
    @GetMapping("/high-confidence")
    public ResponseEntity<List<DetectionRecord>> getHighConfidenceDetections(
            @RequestParam(defaultValue = "0.8") Double threshold) {
        List<DetectionRecord> records = detectionService.getHighConfidenceDetections(threshold);
        return ResponseEntity.ok(records);
    }
    
    /**
     * 删除检测记录
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteDetection(@PathVariable Long id) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            if (detectionService.findById(id).isPresent()) {
                detectionService.deleteRecord(id);
                response.put("success", true);
                response.put("message", "检测记录删除成功");
                return ResponseEntity.ok(response);
            } else {
                response.put("success", false);
                response.put("message", "检测记录不存在");
                return ResponseEntity.notFound().build();
            }
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "删除失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 获取检测统计信息
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getDetectionStats() {
        Map<String, Object> stats = new HashMap<>();
        
        try {
            List<Object[]> diseaseStats = detectionService.getDiseaseTypeStatistics();
            stats.put("diseaseTypeStatistics", diseaseStats);
            stats.put("success", true);
            
            return ResponseEntity.ok(stats);
            
        } catch (Exception e) {
            stats.put("success", false);
            stats.put("message", "获取统计信息失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(stats);
        }
    }
    
    /**
     * 获取用户检测统计
     */
    @GetMapping("/stats/user/{userId}")
    public ResponseEntity<Map<String, Object>> getUserDetectionStats(@PathVariable Long userId) {
        Map<String, Object> stats = new HashMap<>();
        
        try {
            long detectionCount = detectionService.countDetectionsByUser(userId);
            stats.put("totalDetections", detectionCount);
            stats.put("userId", userId);
            stats.put("success", true);
            
            return ResponseEntity.ok(stats);
            
        } catch (Exception e) {
            stats.put("success", false);
            stats.put("message", "获取用户统计信息失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(stats);
        }
    }
}
