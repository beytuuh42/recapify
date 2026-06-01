package com.recapify.llm;

import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class LlmControllerTest {

    @Test
    void returnsSummaryFromService() {
        String prompt = "summarize Breaking Bad season 1 episode 1";
        Summary expectedSummary = new Summary("Walter starts cooking meth.");
        LlmService llmService = mock(LlmService.class);
        LlmController controller = new LlmController(llmService);
        when(llmService.getSummary(prompt)).thenReturn(expectedSummary);

        ResponseEntity<Summary> response = controller.createSummary(prompt);

        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(response.getBody()).isEqualTo(expectedSummary);
        verify(llmService).getSummary(prompt);
    }
}
