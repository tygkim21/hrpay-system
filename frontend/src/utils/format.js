/** 금액 포맷: 3000000 → "3,000,000원" */
export const formatCurrency = (value) => {
    if (value === null || value === undefined) return '-';
    return `${Number(value).toLocaleString('ko-KR')}원`;
};

/** 날짜 포맷: "2024-01-01" → "2024년 01월 01일" */
export const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('ko-KR', {
        year : 'numeric',
        month: '2-digit',
        day  : '2-digit',
    });
};

/** 주민번호 마스킹: 901010-1234567 → "901010-1******" */
export const maskResidentNo = (no) => {
    if (!no || no.length < 7) return no;
    return `${no.substring(0, 7)}******`;
};
