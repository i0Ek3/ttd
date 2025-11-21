# Security Policy

## Supported Versions

We take security seriously and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Yes             |
| 0.2.x   | ❌ No              |
| < 0.2   | ❌ No              |

## Reporting a Vulnerability

If you discover a security vulnerability in TTD, please report it responsibly:

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Contact Gary19gts directly through:
   - Email: [Create a private issue or contact through Ko-fi]
   - Ko-fi: https://ko-fi.com/gary19gts (private message)

### What to Include

Please include the following information in your report:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** of the vulnerability
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (1-30 days)

## Security Best Practices

### For Users

1. **Download Only Trusted Content**
   - Only download your own content or content you have permission to download
   - Verify URLs before downloading
   - Be cautious with shortened URLs

2. **Keep Software Updated**
   - Always use the latest version of TTD
   - Keep Python and dependencies updated
   - Regularly update yt-dlp engine

3. **Safe Download Practices**
   - Choose a secure download location
   - Scan downloaded files if suspicious
   - Don't download to system directories

### For Developers

1. **Input Validation**
   - All URLs are validated before processing
   - File names are sanitized to prevent path traversal
   - User inputs are properly escaped

2. **Network Security**
   - HTTPS connections when possible
   - Proper error handling for network failures
   - No sensitive data in logs

3. **File System Security**
   - Safe file writing practices
   - Proper permissions on created files
   - No execution of downloaded content

## Known Security Considerations

### Current Limitations

1. **URL Validation**: While we validate TikTok URLs, malicious redirects could potentially be an issue
2. **File Names**: Downloaded files use names from TikTok metadata, which could contain special characters
3. **Network Requests**: The application makes network requests to TikTok servers

### Mitigations in Place

1. **URL Sanitization**: URLs are validated against known TikTok patterns
2. **File Name Cleaning**: Special characters are removed from file names
3. **Error Handling**: Network errors are caught and handled gracefully
4. **No Code Execution**: Downloaded content is never executed

## Responsible Disclosure

We believe in responsible disclosure and will:

1. **Acknowledge** your report within 48 hours
2. **Investigate** the issue thoroughly
3. **Provide updates** on our progress
4. **Credit you** in our security advisories (if desired)
5. **Release fixes** as soon as safely possible

## Security Updates

Security updates will be:

- Released as patch versions (e.g., 1.0.1 → 1.0.2)
- Announced in release notes
- Highlighted in the README
- Distributed through normal update channels

## Contact

For security-related inquiries:
- **Primary**: Ko-fi private message → https://ko-fi.com/gary19gts
- **Alternative**: Create a private repository issue

---

**Thank you for helping keep TTD secure!**

*Last updated: October 2025*