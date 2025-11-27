package com.graduation.cropdisease.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "detection_records")
public class DetectionRecord {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;
    
    @Column(name = "image_path")
    private String imagePath;
    
    @Column(name = "detected_disease")
    private String detectedDisease;
    
    @Column(name = "crop_type")
    private String cropType;
    
    @Column
    private Double confidence;
    
    @Column(name = "treatment_method", columnDefinition = "TEXT")
    private String treatmentMethod;
    
    @Column(name = "severity_level")
    private String severityLevel;
    
    @Column(columnDefinition = "TEXT")
    private String recommendations;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
    
    // 构造函数
    public DetectionRecord() {}
    
    public DetectionRecord(User user, String imagePath, String detectedDisease, 
                          String cropType, Double confidence) {
        this.user = user;
        this.imagePath = imagePath;
        this.detectedDisease = detectedDisease;
        this.cropType = cropType;
        this.confidence = confidence;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public User getUser() {
        return user;
    }
    
    public void setUser(User user) {
        this.user = user;
    }
    
    public String getImagePath() {
        return imagePath;
    }
    
    public void setImagePath(String imagePath) {
        this.imagePath = imagePath;
    }
    
    public String getDetectedDisease() {
        return detectedDisease;
    }
    
    public void setDetectedDisease(String detectedDisease) {
        this.detectedDisease = detectedDisease;
    }
    
    public String getCropType() {
        return cropType;
    }
    
    public void setCropType(String cropType) {
        this.cropType = cropType;
    }
    
    public Double getConfidence() {
        return confidence;
    }
    
    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }
    
    public String getTreatmentMethod() {
        return treatmentMethod;
    }
    
    public void setTreatmentMethod(String treatmentMethod) {
        this.treatmentMethod = treatmentMethod;
    }
    
    public String getSeverityLevel() {
        return severityLevel;
    }
    
    public void setSeverityLevel(String severityLevel) {
        this.severityLevel = severityLevel;
    }
    
    public String getRecommendations() {
        return recommendations;
    }
    
    public void setRecommendations(String recommendations) {
        this.recommendations = recommendations;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}