// Toggle Lab Mode
export const LAB_CONFIG = {
    default: {
        title: 'Context Engineering with Redis & LangChain',
        hero: {
            tagline: 'Context Engineering with Redis & LangChain',
            subtitle: 'Engineer every layer of context as you evolve a course advisor agent from baseline RAG to a full agent',
            homeLink: '/intro/welcome/'
        },
        sidebar: [
            {
                label: 'Introduction',
                items: [
                    'intro/welcome',
                    'intro/getting-started',
                ]
            },
            {
                label: 'Wrap up',
                items: [
                    'wrap-up/finish-lab'
                ]
            }
        ]
    }
};

export const config = LAB_CONFIG.default;

