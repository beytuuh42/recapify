package com.recapify.llm;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/llm")
public class LlmController {

    private final LlmService llmService;

    @Autowired
    public LlmController(LlmService llmService) {
        this.llmService = llmService;
    }

    @PostMapping("/summary")
    ResponseEntity<Summary> createSummary(@RequestBody String text) {
        Summary res = llmService.getSummary(text);
        return ResponseEntity.ok(res);
    }
}
