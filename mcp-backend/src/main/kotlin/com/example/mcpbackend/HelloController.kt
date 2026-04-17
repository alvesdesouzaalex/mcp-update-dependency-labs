package com.example.mcpbackend

import org.springframework.web.bind.annotation.CrossOrigin
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@RestController
@CrossOrigin(origins = ["http://localhost:5173"])
class HelloController {

    private val formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss")

    @GetMapping("/hello")
    fun hello(@RequestParam(defaultValue = "World") name: String): String {
        val now = LocalDateTime.now().format(formatter)
        return "Hello $name: agora sao: $now"
    }
}
