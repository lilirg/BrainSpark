package com.brainspark.repository;

import com.brainspark.entity.User;
import com.brainspark.entity.User.Role;
import com.brainspark.entity.User.UserStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
    Page<User> findByRole(Role role, Pageable pageable);
    Page<User> findByStatus(UserStatus status, Pageable pageable);
    Page<User> findByRoleAndStatus(Role role, UserStatus status, Pageable pageable);
}