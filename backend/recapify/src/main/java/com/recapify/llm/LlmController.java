package com.recapify.llm;

import com.recapify.llm.dto.SummaryResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Slf4j
@RequiredArgsConstructor
@RequestMapping("/api/v1/llm")
public class LlmController {

    private final LlmService llmService;

    @PostMapping("/summary")
    ResponseEntity<SummaryResponse> createSummary(@RequestBody String text) {
        log.info("Summary request received textLength={}", text.length());
        SummaryResponse summary = llmService.getSummary(text);
        log.info("Summary request completed finalSummaryLength={} keyEventsCount={}",
                summary.finalSummary().length(), summary.keyEvents().size());
        return ResponseEntity.ok(summary);
    }
}
