# Java Microservice Surface Checklist

| Signal | Where to look |
|--------|----------------|
| REST API | `@RestController`, `@Controller`, Spring Web |
| Auth | `@PreAuthorize`, Spring Security config, filters |
| SQL | MyBatis mappers, JdbcTemplate, JPA repositories |
| Command exec | `Runtime.getRuntime().exec`, `ProcessBuilder` |
| File IO | `MultipartFile`, `Files.read`, zip extract |
| Outbound HTTP | `@FeignClient`, `RestTemplate`, `WebClient` |
| Messaging | `@KafkaListener`, Rabbit templates |
| Config secrets | `application.yml`, env placeholders |
