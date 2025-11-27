package com.graduation.cropdisease.service;

import com.graduation.cropdisease.entity.User;
import com.graduation.cropdisease.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {
    
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    /**
     * 创建新用户
     */
    public User createUser(User user) {
        user.setCreatedAt(LocalDateTime.now());
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }
    
    /**
     * 根据ID查找用户
     */
    public Optional<User> findById(Long id) {
        if (id == null) {
            return Optional.empty();
        }
        return userRepository.findById(id);
    }
    
    /**
     * 根据用户名查找用户
     */
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }
    
    /**
     * 根据邮箱查找用户
     */
    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }
    
    /**
     * 检查用户名是否存在
     */
    public boolean isUsernameExists(String username) {
        return userRepository.existsByUsername(username);
    }
    
    /**
     * 检查邮箱是否存在
     */
    public boolean isEmailExists(String email) {
        return userRepository.existsByEmail(email);
    }
    
    /**
     * 获取所有用户
     */
    public List<User> findAllUsers() {
        return userRepository.findAll();
    }
    
    /**
     * 更新用户信息
     */
    public User updateUser(User user) {
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }
    
    /**
     * 删除用户
     */
    public void deleteUser(Long id) {
        if (id != null) {
            userRepository.deleteById(id);
        }
    }
    
    /**
     * 统计用户总数
     */
    public long countUsers() {
        return userRepository.countAllUsers();
    }
    
    /**
     * 用户登录验证
     */
    public boolean validateUser(String username, String password) {
        Optional<User> userOpt = findByUsername(username);
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            // 这里应该使用加密密码比较，暂时使用简单比较
            return password.equals(user.getPassword());
        }
        return false;
    }
    
    /**
     * 用户注册
     */
    public User registerUser(String username, String password, String email, String realName) {
        if (isUsernameExists(username)) {
            throw new RuntimeException("用户名已存在");
        }
        if (isEmailExists(email)) {
            throw new RuntimeException("邮箱已被注册");
        }
        
        User user = new User();
        user.setUsername(username);
        user.setPassword(password); // 实际应用中应该加密
        user.setEmail(email);
        user.setRealName(realName);
        
        return createUser(user);
    }
}
