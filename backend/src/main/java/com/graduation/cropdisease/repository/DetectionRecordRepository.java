package com.graduation.cropdisease.repository;

import com.graduation.cropdisease.entity.DetectionRecord;
import com.graduation.cropdisease.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface DetectionRecordRepository extends JpaRepository<DetectionRecord, Long> {
    
    /**
     * 根据用户查找检测记录
     */
    List<DetectionRecord> findByUser(User user);
    
    /**
     * 根据用户ID查找检测记录
     */
    List<DetectionRecord> findByUserId(Long userId);
    
    /**
     * 根据疾病类型查找记录
     */
    List<DetectionRecord> findByDetectedDisease(String detectedDisease);
    
    /**
     * 根据置信度范围查找记录
     */
    @Query("SELECT d FROM DetectionRecord d WHERE d.confidence BETWEEN :minConfidence AND :maxConfidence")
    List<DetectionRecord> findByConfidenceRange(@Param("minConfidence") Double minConfidence, 
                                               @Param("maxConfidence") Double maxConfidence);
    
    /**
     * 根据时间范围查找记录
     */
    @Query("SELECT d FROM DetectionRecord d WHERE d.createdAt BETWEEN :startTime AND :endTime")
    List<DetectionRecord> findByCreatedAtRange(@Param("startTime") LocalDateTime startTime,
                                               @Param("endTime") LocalDateTime endTime);
    
    /**
     * 统计用户检测次数
     */
    @Query("SELECT COUNT(d) FROM DetectionRecord d WHERE d.user.id = :userId")
    long countByUserId(@Param("userId") Long userId);
    
    /**
     * 查找最近的检测记录
     */
    @Query("SELECT d FROM DetectionRecord d ORDER BY d.createdAt DESC")
    List<DetectionRecord> findRecentDetections();
    
    /**
     * 统计每种疾病的检测次数
     */
    @Query("SELECT d.detectedDisease, COUNT(d) FROM DetectionRecord d GROUP BY d.detectedDisease")
    List<Object[]> countByDiseaseType();
}
