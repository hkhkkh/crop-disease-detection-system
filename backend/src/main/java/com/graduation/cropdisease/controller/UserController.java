package com.graduation.cropdisease.controller;

import com.graduation.cropdisease.entity.User;
import com.graduation.cropdisease.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    /**
     * 获取所有用户
     */
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.findAllUsers();
        return ResponseEntity.ok(users);
    }
    
    /**
     * 根据ID获取用户
     */
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        Optional<User> user = userService.findById(id);
        return user.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * 创建新用户
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createUser(@RequestBody User user) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            if (userService.isUsernameExists(user.getUsername())) {
                response.put("success", false);
                response.put("message", "用户名已存在");
                return ResponseEntity.badRequest().body(response);
            }
            
            if (userService.isEmailExists(user.getEmail())) {
                response.put("success", false);
                response.put("message", "邮箱已被注册");
                return ResponseEntity.badRequest().body(response);
            }
            
            User createdUser = userService.createUser(user);
            response.put("success", true);
            response.put("message", "用户创建成功");
            response.put("user", createdUser);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "创建用户失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 用户登录
     */
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> loginData) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            String username = loginData.get("username");
            String password = loginData.get("password");
            
            if (userService.validateUser(username, password)) {
                Optional<User> userOpt = userService.findByUsername(username);
                response.put("success", true);
                response.put("message", "登录成功");
                response.put("user", userOpt.get());
            } else {
                response.put("success", false);
                response.put("message", "用户名或密码错误");
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "登录失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 用户注册
     */
    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody Map<String, String> registerData) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            String username = registerData.get("username");
            String password = registerData.get("password");
            String email = registerData.get("email");
            String realName = registerData.get("realName");
            
            User user = userService.registerUser(username, password, email, realName);
            
            response.put("success", true);
            response.put("message", "注册成功");
            response.put("user", user);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 更新用户信息
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateUser(@PathVariable Long id, @RequestBody User user) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            Optional<User> existingUser = userService.findById(id);
            if (existingUser.isPresent()) {
                user.setId(id);
                User updatedUser = userService.updateUser(user);
                
                response.put("success", true);
                response.put("message", "用户信息更新成功");
                response.put("user", updatedUser);
                
                return ResponseEntity.ok(response);
            } else {
                response.put("success", false);
                response.put("message", "用户不存在");
                return ResponseEntity.notFound().build();
            }
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "更新失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 删除用户
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteUser(@PathVariable Long id) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            if (userService.findById(id).isPresent()) {
                userService.deleteUser(id);
                response.put("success", true);
                response.put("message", "用户删除成功");
                return ResponseEntity.ok(response);
            } else {
                response.put("success", false);
                response.put("message", "用户不存在");
                return ResponseEntity.notFound().build();
            }
            
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "删除失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }
    
    /**
     * 获取用户统计信息
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getUserStats() {
        Map<String, Object> stats = new HashMap<>();
        
        try {
            long totalUsers = userService.countUsers();
            stats.put("totalUsers", totalUsers);
            stats.put("success", true);
            
            return ResponseEntity.ok(stats);
            
        } catch (Exception e) {
            stats.put("success", false);
            stats.put("message", "获取统计信息失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(stats);
        }
    }
}
