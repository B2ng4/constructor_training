//Для сортировки в метод sort
export const createComparator = (fieldName) => (a, b) => a[fieldName] - b[fieldName];