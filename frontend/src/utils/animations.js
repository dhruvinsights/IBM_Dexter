/**
 * Animation Utilities for IBM Dexter Frontend
 * Provides consistent, subtle animations using Framer Motion
 * Following IBM Carbon motion principles
 */

// IBM Carbon motion durations (in seconds)
export const DURATION = {
  fast01: 0.07,
  fast02: 0.11,
  moderate01: 0.15,
  moderate02: 0.24,
  slow01: 0.4,
  slow02: 0.7,
};

// IBM Carbon motion easings
export const EASING = {
  standard: {
    productive: [0.2, 0, 0.38, 0.9],
    expressive: [0.4, 0.14, 0.3, 1],
  },
  entrance: {
    productive: [0, 0, 0.38, 0.9],
    expressive: [0, 0, 0.3, 1],
  },
  exit: {
    productive: [0.2, 0, 1, 0.9],
    expressive: [0.4, 0.14, 1, 1],
  },
};

/**
 * Page Transitions
 * Subtle fade and slide for page navigation
 */
export const pageTransition = {
  initial: { 
    opacity: 0, 
    y: 20 
  },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: DURATION.moderate02,
      ease: EASING.entrance.productive,
    }
  },
  exit: { 
    opacity: 0, 
    y: -20,
    transition: {
      duration: DURATION.moderate01,
      ease: EASING.exit.productive,
    }
  },
};

/**
 * Card Hover Animation
 * Subtle lift effect on hover
 */
export const cardHover = {
  whileHover: { 
    y: -4,
    transition: { 
      duration: DURATION.fast02,
      ease: EASING.standard.productive,
    }
  },
  whileTap: {
    y: -2,
    transition: { 
      duration: DURATION.fast01,
      ease: EASING.standard.productive,
    }
  },
};

/**
 * Skeleton Pulse Animation
 * Loading state pulse effect
 */
export const skeletonPulse = {
  animate: { 
    opacity: [0.5, 1, 0.5] 
  },
  transition: { 
    duration: DURATION.slow02 * 2,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

/**
 * Toast/Notification Slide-in
 * Slide from right for notifications
 */
export const toastSlide = {
  initial: { 
    x: 400, 
    opacity: 0 
  },
  animate: { 
    x: 0, 
    opacity: 1,
    transition: {
      duration: DURATION.moderate02,
      ease: EASING.entrance.expressive,
    }
  },
  exit: { 
    x: 400, 
    opacity: 0,
    transition: {
      duration: DURATION.moderate01,
      ease: EASING.exit.expressive,
    }
  },
};

/**
 * Fade In Animation
 * Simple fade in for content
 */
export const fadeIn = {
  initial: { 
    opacity: 0 
  },
  animate: { 
    opacity: 1,
    transition: {
      duration: DURATION.moderate01,
      ease: EASING.entrance.productive,
    }
  },
  exit: { 
    opacity: 0,
    transition: {
      duration: DURATION.fast02,
      ease: EASING.exit.productive,
    }
  },
};

/**
 * Scale In Animation
 * Subtle scale effect for modals/dialogs
 */
export const scaleIn = {
  initial: { 
    opacity: 0, 
    scale: 0.95 
  },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: {
      duration: DURATION.moderate02,
      ease: EASING.entrance.expressive,
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.95,
    transition: {
      duration: DURATION.moderate01,
      ease: EASING.exit.expressive,
    }
  },
};

/**
 * List Item Stagger
 * Staggered animation for list items
 */
export const listStagger = {
  container: {
    animate: {
      transition: {
        staggerChildren: 0.05,
      },
    },
  },
  item: {
    initial: { 
      opacity: 0, 
      x: -20 
    },
    animate: { 
      opacity: 1, 
      x: 0,
      transition: {
        duration: DURATION.moderate01,
        ease: EASING.entrance.productive,
      }
    },
  },
};

/**
 * Slide Up Animation
 * Slide up from bottom
 */
export const slideUp = {
  initial: { 
    opacity: 0, 
    y: 40 
  },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: DURATION.moderate02,
      ease: EASING.entrance.productive,
    }
  },
  exit: { 
    opacity: 0, 
    y: 40,
    transition: {
      duration: DURATION.moderate01,
      ease: EASING.exit.productive,
    }
  },
};

/**
 * Expand/Collapse Animation
 * For accordion-like components
 */
export const expandCollapse = {
  initial: { 
    height: 0, 
    opacity: 0 
  },
  animate: { 
    height: 'auto', 
    opacity: 1,
    transition: {
      height: {
        duration: DURATION.moderate02,
        ease: EASING.standard.productive,
      },
      opacity: {
        duration: DURATION.moderate01,
        ease: EASING.entrance.productive,
      },
    }
  },
  exit: { 
    height: 0, 
    opacity: 0,
    transition: {
      height: {
        duration: DURATION.moderate01,
        ease: EASING.standard.productive,
      },
      opacity: {
        duration: DURATION.fast02,
        ease: EASING.exit.productive,
      },
    }
  },
};

/**
 * Button Press Animation
 * Subtle scale on button press
 */
export const buttonPress = {
  whileTap: { 
    scale: 0.98,
    transition: {
      duration: DURATION.fast01,
      ease: EASING.standard.productive,
    }
  },
};

/**
 * Rotate Animation
 * For loading spinners
 */
export const rotate = {
  animate: {
    rotate: 360,
  },
  transition: {
    duration: 1,
    repeat: Infinity,
    ease: 'linear',
  },
};

/**
 * Pulse Animation
 * For attention-grabbing elements
 */
export const pulse = {
  animate: {
    scale: [1, 1.05, 1],
  },
  transition: {
    duration: DURATION.slow01 * 2,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

// Export all animations as a single object for convenience
export const animations = {
  pageTransition,
  cardHover,
  skeletonPulse,
  toastSlide,
  fadeIn,
  scaleIn,
  listStagger,
  slideUp,
  expandCollapse,
  buttonPress,
  rotate,
  pulse,
};

export default animations;

// Made with Bob
