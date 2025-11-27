package com.graduation.cropdisease;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class CropDiseaseApplication {

    public static void main(String[] args) {
        SpringApplication.run(CropDiseaseApplication.class, args);
        System.out.println("🌱 作物病害检测系统启动成功!");
        System.out.println("📡 API地址: http://localhost:8080");
        System.out.println("🔍 健康检查: http://localhost:8080/api/system/health");
    }

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}