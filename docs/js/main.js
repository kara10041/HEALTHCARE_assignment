/**
 * WriteFlow AI - Interactive Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  initPricingToggle();
  initFaqAccordion();
  initMobileMenu();
  initDemoModal();
  initTrialActions();
});

/* ==========================================================================
   1. Pricing Toggle (Monthly vs Yearly)
   ========================================================================== */
function initPricingToggle() {
  const toggleButtons = document.querySelectorAll('.pricing-toggle-btn');
  const proPriceEl = document.getElementById('price-pro');
  const enterprisePriceEl = document.getElementById('price-enterprise');
  const proPeriodEl = document.getElementById('period-pro');
  const enterprisePeriodEl = document.getElementById('period-enterprise');

  if (!toggleButtons.length) return;

  const prices = {
    monthly: {
      pro: '$19',
      proPeriod: '/월',
      enterprise: '$49',
      enterprisePeriod: '/월'
    },
    yearly: {
      pro: '$15',
      proPeriod: '/월 (연간 청구 $180)',
      enterprise: '$39',
      enterprisePeriod: '/월 (연간 청구 $468)'
    }
  };

  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      toggleButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const planType = btn.dataset.plan || 'monthly';
      
      // Animate price change
      if (proPriceEl && prices[planType]) {
        animateValue(proPriceEl, prices[planType].pro);
        if (proPeriodEl) proPeriodEl.textContent = prices[planType].proPeriod;
      }
      if (enterprisePriceEl && prices[planType]) {
        animateValue(enterprisePriceEl, prices[planType].enterprise);
        if (enterprisePeriodEl) enterprisePeriodEl.textContent = prices[planType].enterprisePeriod;
      }
    });
  });
}

function animateValue(element, targetText) {
  element.style.opacity = '0';
  element.style.transform = 'translateY(-6px)';
  setTimeout(() => {
    element.textContent = targetText;
    element.style.transition = 'all 0.25s ease';
    element.style.opacity = '1';
    element.style.transform = 'translateY(0)';
  }, 150);
}

/* ==========================================================================
   2. FAQ Accordion
   ========================================================================== */
function initFaqAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question-btn');
    if (!questionBtn) return;

    questionBtn.addEventListener('click', () => {
      const isOpen = item.classList.contains('active');

      // Close all other accordions
      faqItems.forEach(otherItem => {
        if (otherItem !== item) {
          otherItem.classList.remove('active');
        }
      });

      // Toggle current
      if (isOpen) {
        item.classList.remove('active');
      } else {
        item.classList.add('active');
      }
    });
  });
}

/* ==========================================================================
   3. Mobile Navigation Drawer
   ========================================================================== */
function initMobileMenu() {
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const closeMenuBtn = document.getElementById('closeMenuBtn');
  const drawer = document.getElementById('mobileNavDrawer');
  const overlay = document.getElementById('mobileNavOverlay');
  const drawerLinks = document.querySelectorAll('.mobile-drawer-link');

  function openDrawer() {
    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawer.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openDrawer);
  if (closeMenuBtn) closeMenuBtn.addEventListener('click', closeDrawer);
  if (overlay) overlay.addEventListener('click', closeDrawer);

  drawerLinks.forEach(link => {
    link.addEventListener('click', closeDrawer);
  });
}

/* ==========================================================================
   4. Live AI Writing Demo Modal & Simulator
   ========================================================================== */
function initDemoModal() {
  const demoModalBackdrop = document.getElementById('demoModalBackdrop');
  const openDemoBtns = document.querySelectorAll('[data-action="open-demo"]');
  const closeDemoBtn = document.getElementById('closeDemoModalBtn');
  const promptChips = document.querySelectorAll('.demo-chip');
  const demoInput = document.getElementById('demoInput');
  const generateBtn = document.getElementById('demoGenerateBtn');
  const outputText = document.getElementById('demoOutputText');

  if (!demoModalBackdrop) return;

  const presets = {
    blog: {
      prompt: '2026년 생성형 AI 트렌드와 생산성 향상 방안에 대한 매력적인 블로그 도입부',
      result: `인공지능이 업무 환경을 재정의하고 있는 오늘날, '얼마나 빨리 쓰느냐'보다 '얼마나 효과적으로 협업하느냐'가 핵심 경쟁력입니다. \n\nWriteFlow AI는 단순한 텍스트 생성을 넘어 사용자의 생각과 문체를 가장 자연스럽게 확장해 줍니다. 지금 바로 스마트한 글쓰기의 새로운 기준을 경험해 보세요.`
    },
    email: {
      prompt: '신규 기능 출시 안내 및 VIP 고객 초대 비즈니스 뉴스레터 이메일',
      result: `제목: [초대] 귀하의 비즈니스 생산성을 3배 높여줄 WriteFlow 2.0이 공개되었습니다.\n\n안녕하세요, 파트너님.\n항상 저희와 함께해 주셔서 감사합니다. 이번에 선보이는 새로운 협업 엔진과 맞춤형 톤앤매너 기능을 가장 먼저 체험해 보실 수 있는 VIP 얼리억세스에 초대합니다.`
    },
    ad: {
      prompt: '인스타그램/페이스북용 2030 직장인 타깃 AI 글쓰기 툴 광고 카피',
      result: `💡 "아직도 기획서 쓰느라 야근하세요?"\n\n아이디어 키워드만 던지면 10초 만에 전문적인 제안서와 카피가 완성됩니다.\n당신의 퇴근 시간을 앞당겨줄 궁극의 AI 파트너, WriteFlow와 함께 스마트하게 일하세요! ✨`
    },
    translate: {
      prompt: '해외 바이어를 위한 제품 소개서 영문 글로벌 번역 및 현지화',
      result: `Subject: Introducing WriteFlow - Redefining AI-Powered Enterprise Content Creation\n\nTransform raw brainstorms into polished executive communications in seconds. Our state-of-the-art neural engine delivers exceptional clarity and precision across 50+ languages.`
    }
  };

  let typingTimer = null;

  function openModal() {
    demoModalBackdrop.classList.add('active');
    document.body.style.overflow = 'hidden';
    // Run initial generation if empty
    if (!outputText.dataset.generated) {
      runSimulation(presets.blog.result);
      outputText.dataset.generated = 'true';
    }
  }

  function closeModal() {
    demoModalBackdrop.classList.remove('active');
    document.body.style.overflow = '';
    if (typingTimer) clearInterval(typingTimer);
  }

  openDemoBtns.forEach(btn => btn.addEventListener('click', (e) => {
    e.preventDefault();
    openModal();
  }));

  if (closeDemoBtn) closeDemoBtn.addEventListener('click', closeModal);
  demoModalBackdrop.addEventListener('click', (e) => {
    if (e.target === demoModalBackdrop) closeModal();
  });

  // Prompt chips selection
  promptChips.forEach(chip => {
    chip.addEventListener('click', () => {
      promptChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      const presetKey = chip.dataset.preset;
      if (presets[presetKey]) {
        demoInput.value = presets[presetKey].prompt;
        runSimulation(presets[presetKey].result);
      }
    });
  });

  // Generate button click
  if (generateBtn) {
    generateBtn.addEventListener('click', () => {
      const customPrompt = demoInput.value.trim();
      if (!customPrompt) {
        showToast('프롬프트를 입력하거나 추천 키워드를 선택해 주세요.', 'info');
        return;
      }
      const sampleText = `✨ [AI 생성 결과]: "${customPrompt}"\n\nWriteFlow AI가 사용자의 의도를 분석하여 전문적이고 완성도 높은 콘텐츠를 생성했습니다. 문맥에 최적화된 어조와 정확한 문법 구조가 자동으로 적용되었습니다.`;
      runSimulation(sampleText);
    });
  }

  // Realistic typewriter effect
  function runSimulation(fullText) {
    if (typingTimer) clearInterval(typingTimer);
    outputText.innerHTML = '<span class="cursor"></span>';
    generateBtn.disabled = true;
    generateBtn.style.opacity = '0.7';

    let index = 0;
    const speed = 18;

    typingTimer = setInterval(() => {
      if (index < fullText.length) {
        index++;
        const currentText = fullText.slice(0, index);
        outputText.innerHTML = escapeHtml(currentText) + '<span class="cursor"></span>';
      } else {
        clearInterval(typingTimer);
        outputText.innerHTML = escapeHtml(fullText);
        generateBtn.disabled = false;
        generateBtn.style.opacity = '1';
      }
    }, speed);
  }
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

/* ==========================================================================
   5. User Actions & Interactive Toast
   ========================================================================== */
function initTrialActions() {
  const trialButtons = document.querySelectorAll('[data-action="start-trial"]');
  const contactButtons = document.querySelectorAll('[data-action="contact-sales"]');

  trialButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      showToast('🎉 14일 무료 체험이 활성화되었습니다! 신용카드 등록 없이 바로 시작하세요.', 'success');
    });
  });

  contactButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      showToast('📩 영업팀 문의가 접수되었습니다. 담당자가 24시간 내 연락드리겠습니다.', 'success');
    });
  });
}

function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast';
  
  const iconName = type === 'success' ? 'check_circle' : 'info';
  toast.innerHTML = `
    <span class="material-symbols-outlined">${iconName}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  // Auto dismiss
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, 4000);
}
