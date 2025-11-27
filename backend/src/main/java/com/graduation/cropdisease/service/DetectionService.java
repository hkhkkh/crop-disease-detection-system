package com.graduation.cropdisease.service;

import com.graduation.cropdisease.entity.DetectionRecord;
import com.graduation.cropdisease.entity.User;
import com.graduation.cropdisease.repository.DetectionRecordRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class DetectionService {
    
    @Autowired
    private DetectionRecordRepository detectionRecordRepository;
    
    /**
     * 创建检测记录
     */
    public DetectionRecord createDetectionRecord(DetectionRecord record) {
        record.setCreatedAt(LocalDateTime.now());
        return detectionRecordRepository.save(record);
    }
    
    /**
     * 根据ID查找检测记录
     */
    public Optional<DetectionRecord> findById(Long id) {
        return detectionRecordRepository.findById(id);
    }
    
    /**
     * 根据用户查找检测记录
     */
    public List<DetectionRecord> findByUser(User user) {
        return detectionRecordRepository.findByUser(user);
    }
    
    /**
     * 根据用户ID查找检测记录
     */
    public List<DetectionRecord> findByUserId(Long userId) {
        return detectionRecordRepository.findByUserId(userId);
    }
    
    /**
     * 根据疾病类型查找记录
     */
    public List<DetectionRecord> findByDiseaseType(String diseaseType) {
        return detectionRecordRepository.findByDetectedDisease(diseaseType);
    }
    
    /**
     * 获取所有检测记录
     */
    public List<DetectionRecord> findAllRecords() {
        return detectionRecordRepository.findAll();
    }
    
    /**
     * 获取最近的检测记录
     */
    public List<DetectionRecord> getRecentDetections() {
        return detectionRecordRepository.findRecentDetections();
    }
    
    /**
     * 统计用户检测次数
     */
    public long countDetectionsByUser(Long userId) {
        return detectionRecordRepository.countByUserId(userId);
    }
    
    /**
     * 统计疾病类型分布
     */
    public List<Object[]> getDiseaseTypeStatistics() {
        return detectionRecordRepository.countByDiseaseType();
    }
    
    /**
     * 根据置信度范围查找记录
     */
    public List<DetectionRecord> findByConfidenceRange(Double minConfidence, Double maxConfidence) {
        return detectionRecordRepository.findByConfidenceRange(minConfidence, maxConfidence);
    }
    
    /**
     * 根据时间范围查找记录
     */
    public List<DetectionRecord> findByTimeRange(LocalDateTime startTime, LocalDateTime endTime) {
        return detectionRecordRepository.findByCreatedAtRange(startTime, endTime);
    }
    
    /**
     * 删除检测记录
     */
    public void deleteRecord(Long id) {
        detectionRecordRepository.deleteById(id);
    }
    
    /**
     * 保存检测结果
     */
    public DetectionRecord saveDetectionResult(User user, String imagePath, String detectedDisease, 
                                             Double confidence, String recommendations) {
        DetectionRecord record = new DetectionRecord();
        record.setUser(user);
        record.setImagePath(imagePath);
        record.setDetectedDisease(detectedDisease);
        record.setConfidence(confidence);
        record.setRecommendations(recommendations);
        
        return createDetectionRecord(record);
    }
    
    /**
     * 获取高置信度检测结果
     */
    public List<DetectionRecord> getHighConfidenceDetections(Double threshold) {
        return findByConfidenceRange(threshold, 1.0);
    }
    
    /**
     * 获取用户最近的检测记录
     */
    public List<DetectionRecord> getUserRecentDetections(Long userId, int limit) {
        List<DetectionRecord> userRecords = findByUserId(userId);
        return userRecords.stream()
                .sorted((r1, r2) -> r2.getCreatedAt().compareTo(r1.getCreatedAt()))
                .limit(limit)
                .toList();
    }
}
